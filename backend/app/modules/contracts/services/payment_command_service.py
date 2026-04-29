from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.repositories.contract_repo import (
  fetch_contract_id_row,
  fetch_contract_total_amount_row,
  update_contract_paid_amount,
  update_contract_status,
)
from app.modules.contracts.repositories.payment_repo import (
  delete_payment as delete_payment_row,
  fetch_payment_status_row,
  insert_payment,
  mark_payment_confirmed,
  query_confirmed_payment_sum,
)
from app.modules.contracts.services.errors import ContractServiceError


def _recalc_paid_amount(deps: ContractRouterDeps, cur: object, contract_id: str) -> float:
  paid_amount = deps.safe_float_func(query_confirmed_payment_sum(cur, contract_id)['paid'], 0)
  update_contract_paid_amount(cur, contract_id=contract_id, paid_amount=paid_amount, now=deps.now_str_func())
  return paid_amount


def create_payment(
  deps: ContractRouterDeps,
  *,
  contract_id: str,
  payment_no: str,
  payment_amount: float,
  payment_date: str,
  payment_method: int,
  payer_name: str,
  received_by: str,
  remark: str,
) -> bool:
  if not contract_id:
    raise ContractServiceError('合同ID不能为空', 400)
  if payment_amount <= 0:
    raise ContractServiceError('回款金额必须大于0', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_contract_id_row(cur, contract_id):
    conn.close()
    raise ContractServiceError('合同不存在', 404)

  try:
    insert_payment(
      cur,
      payment_id=str(uuid.uuid4()),
      contract_id=contract_id,
      payment_no=payment_no,
      payment_amount=payment_amount,
      payment_date=payment_date,
      payment_method=payment_method,
      payer_name=payer_name,
      received_by=received_by,
      remark=remark,
      create_time=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ContractServiceError('回款单号已存在', 400) from error

  conn.close()
  return True


def confirm_payment(deps: ContractRouterDeps, *, payment_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_payment_status_row(cur, payment_id)
  if not row:
    conn.close()
    raise ContractServiceError('回款记录不存在', 404)
  if deps.safe_int_func(row['status'], 0) == 1:
    conn.close()
    return True

  contract_id = str(row['contract_id'])
  mark_payment_confirmed(cur, payment_id)
  paid_amount = _recalc_paid_amount(deps, cur, contract_id)

  contract_row = fetch_contract_total_amount_row(cur, contract_id)
  total_amount = deps.safe_float_func(contract_row['total_amount'], 0) if contract_row else 0
  if total_amount > 0 and paid_amount >= total_amount:
    update_contract_status(cur, contract_id=contract_id, status=3, now=deps.now_str_func())
  elif paid_amount > 0:
    update_contract_status(cur, contract_id=contract_id, status=2, now=deps.now_str_func())

  conn.commit()
  conn.close()
  return True


def delete_payment(deps: ContractRouterDeps, *, payment_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_payment_status_row(cur, payment_id)
  if not row:
    conn.close()
    raise ContractServiceError('回款记录不存在', 404)
  contract_id = str(row['contract_id'])
  was_confirmed = deps.safe_int_func(row['status'], 0) == 1

  delete_payment_row(cur, payment_id)
  if was_confirmed:
    paid_amount = _recalc_paid_amount(deps, cur, contract_id)
    contract_row = fetch_contract_total_amount_row(cur, contract_id)
    total_amount = deps.safe_float_func(contract_row['total_amount'], 0) if contract_row else 0
    if paid_amount <= 0:
      update_contract_status(cur, contract_id=contract_id, status=1, now=deps.now_str_func())
    elif paid_amount < total_amount:
      update_contract_status(cur, contract_id=contract_id, status=2, now=deps.now_str_func())

  conn.commit()
  conn.close()
  return True
