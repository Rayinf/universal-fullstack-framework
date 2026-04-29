from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.helpers import generate_contract_no
from app.modules.contracts.repositories.contract_repo import (
  count_payment_records_by_contract,
  delete_commissions_by_contract,
  delete_contract as delete_contract_row,
  fetch_contract_exists_row,
  fetch_quote_for_contract_conversion,
  insert_contract,
  insert_contract_from_quotation,
  mark_contract_expire_warning_sent,
  query_expiring_contract_rows,
  update_contract as update_contract_row,
  update_contract_terminated,
  update_quotation_status_for_contract,
)
from app.modules.contracts.services.errors import ContractServiceError


def create_contract(
  deps: ContractRouterDeps,
  *,
  contract_no: str,
  quotation_id: str,
  customer_id: str,
  customer_name: str,
  contract_name: str,
  total_amount: float,
  signed_date: str,
  start_date: str,
  end_date: str,
  payment_terms: str,
  contract_status: int,
  remark: str,
) -> bool:
  if not customer_name or not contract_name:
    raise ContractServiceError('客户名称和合同名称不能为空', 400)
  if total_amount < 0:
    raise ContractServiceError('合同金额不能为负数', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  now = deps.now_str_func()
  try:
    insert_contract(
      cur,
      contract_id=str(uuid.uuid4()),
      contract_no=contract_no,
      quotation_id=quotation_id,
      customer_id=customer_id,
      customer_name=customer_name,
      contract_name=contract_name,
      total_amount=total_amount,
      signed_date=signed_date,
      start_date=start_date,
      end_date=end_date,
      payment_terms=payment_terms,
      status=contract_status,
      remark=remark,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ContractServiceError('合同编号已存在', 400) from error

  conn.close()
  return True


def create_contract_from_quotation(
  deps: ContractRouterDeps,
  *,
  quotation_id: str,
  contract_name: str,
  payment_terms: str,
  signed_date: str,
  start_date: str,
  end_date: str,
) -> dict[str, str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  quote = fetch_quote_for_contract_conversion(cur, quotation_id)
  if not quote:
    conn.close()
    raise ContractServiceError('报价单不存在', 404)
  if deps.safe_int_func(quote['status'], 0) != 2:
    conn.close()
    raise ContractServiceError('仅已审批通过的报价单可转合同', 400)

  now = deps.now_str_func()
  contract_id = str(uuid.uuid4())
  contract_no = generate_contract_no()
  resolved_contract_name = contract_name or f"{quote['customer_name'] or ''}采购合同"
  try:
    insert_contract_from_quotation(
      cur,
      contract_id=contract_id,
      contract_no=contract_no,
      quotation_id=quotation_id,
      customer_id=quote['customer_id'] or '',
      customer_name=quote['customer_name'] or '',
      contract_name=resolved_contract_name,
      total_amount=deps.safe_float_func(quote['final_amount'], 0),
      signed_date=signed_date,
      start_date=start_date,
      end_date=end_date,
      payment_terms=payment_terms,
      now=now,
    )
    update_quotation_status_for_contract(cur, quotation_id, status=4, now=now)
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ContractServiceError('生成合同失败，合同编号冲突', 400) from error

  conn.close()
  return {'id': contract_id, 'contractNo': contract_no}


def update_contract(
  deps: ContractRouterDeps,
  *,
  contract_id: str,
  contract_no: str,
  customer_id: str,
  customer_name: str,
  contract_name: str,
  total_amount: float,
  signed_date: str,
  start_date: str,
  end_date: str,
  payment_terms: str,
  contract_status: int,
  remark: str,
) -> bool:
  if not contract_no or not customer_name or not contract_name:
    raise ContractServiceError('合同编号、客户名称、合同名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    update_contract_row(
      cur,
      contract_id=contract_id,
      contract_no=contract_no,
      customer_id=customer_id,
      customer_name=customer_name,
      contract_name=contract_name,
      total_amount=total_amount,
      signed_date=signed_date,
      start_date=start_date,
      end_date=end_date,
      payment_terms=payment_terms,
      status=contract_status,
      remark=remark,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ContractServiceError('合同编号已存在', 400) from error

  conn.close()
  return True


def delete_contract(deps: ContractRouterDeps, *, contract_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  payment_cnt = deps.safe_int_func(count_payment_records_by_contract(cur, contract_id)['cnt'], 0)
  if payment_cnt > 0:
    conn.close()
    raise ContractServiceError('该合同已有关联回款记录，无法删除', 400)
  delete_contract_row(cur, contract_id)
  delete_commissions_by_contract(cur, contract_id)
  conn.commit()
  conn.close()
  return True


def terminate_contract(deps: ContractRouterDeps, *, contract_id: str, remark: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_contract_exists_row(cur, contract_id)
  if not row:
    conn.close()
    raise ContractServiceError('合同不存在', 404)

  update_contract_terminated(cur, contract_id=contract_id, remark=remark, now=deps.now_str_func())
  conn.commit()
  conn.close()
  return True


def check_expiring_contracts(deps: ContractRouterDeps, *, days: int) -> dict[str, int]:
  checked_days = max(1, min(days, 365))
  deadline = (datetime.now() + timedelta(days=checked_days)).strftime('%Y-%m-%d')
  today = datetime.now().strftime('%Y-%m-%d')

  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_expiring_contract_rows(cur, today, deadline)
  notifications: list[dict[str, str]] = []
  warned_contracts = 0
  now = deps.now_str_func()
  for row in rows:
    if deps.safe_int_func(row['expire_warning_sent'], 0) == 1:
      continue
    contract_id = str(row['id'])
    contract_no = str(row['contract_no'] or '')
    end_date = str(row['end_date'] or '')
    notifications.append(
      {
        'contract_id': contract_id,
        'contract_no': contract_no,
        'customer_name': str(row['customer_name'] or '-'),
        'end_date': end_date,
      },
    )
    mark_contract_expire_warning_sent(cur, contract_id=contract_id, now=now)
    warned_contracts += 1

  conn.commit()
  conn.close()

  for item in notifications:
    deps.create_notification_for_users_func(
      ['1'],
      title='合同到期预警',
      content=f'合同 {item["contract_no"]}（客户：{item["customer_name"]}）将于 {item["end_date"]} 到期',
      ntype=2,
      biz_type='contract',
      biz_id=item['contract_id'],
    )

  return {'expiringCount': len(rows), 'newWarnings': warned_contracts, 'days': checked_days}
