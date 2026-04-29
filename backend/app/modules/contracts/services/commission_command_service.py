from __future__ import annotations

import uuid

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.repositories.commission_repo import (
  delete_commission as delete_commission_row,
  fetch_commission_status_row,
  insert_commission,
  update_commission_paid,
)
from app.modules.contracts.repositories.contract_repo import fetch_contract_commission_source
from app.modules.contracts.services.errors import ContractServiceError


def calculate_commission(
  deps: ContractRouterDeps,
  *,
  contract_id: str,
  salesperson_id: str,
  salesperson_name: str,
  commission_rate: float,
  remark: str,
) -> dict[str, float]:
  if commission_rate < 0:
    raise ContractServiceError('佣金比例不能为负数', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  contract = fetch_contract_commission_source(cur, contract_id)
  if not contract:
    conn.close()
    raise ContractServiceError('合同不存在', 404)

  payment_amount = deps.safe_float_func(contract['paid_amount'], 0)
  if payment_amount <= 0:
    conn.close()
    raise ContractServiceError('当前合同暂无已确认回款，无法计算佣金', 400)

  commission_amount = round(payment_amount * commission_rate / 100, 2)
  insert_commission(
    cur,
    commission_id=str(uuid.uuid4()),
    contract_id=contract_id,
    contract_no=contract['contract_no'] or '',
    customer_name=contract['customer_name'] or '',
    salesperson_id=salesperson_id,
    salesperson_name=salesperson_name,
    contract_amount=deps.safe_float_func(contract['total_amount'], 0),
    payment_amount=payment_amount,
    commission_rate=commission_rate,
    commission_amount=commission_amount,
    remark=remark,
    create_time=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return {'commissionAmount': commission_amount}


def pay_commission(deps: ContractRouterDeps, *, commission_id: str, pay_date: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_commission_status_row(cur, commission_id)
  if not row:
    conn.close()
    raise ContractServiceError('佣金记录不存在', 404)

  update_commission_paid(cur, commission_id=commission_id, pay_date=pay_date)
  conn.commit()
  conn.close()
  return True


def delete_commission(deps: ContractRouterDeps, *, commission_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_commission_row(cur, commission_id)
  conn.commit()
  conn.close()
  return True
