from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.customer.deps import CustomerRouterDeps
from app.modules.customer.repositories.customer_repo import (
  delete_customer as delete_customer_row,
  fetch_customer_id,
  fetch_customer_id_by_code_excluding_id,
  insert_customer,
  update_customer as update_customer_row,
)
from app.modules.customer.services.errors import CustomerServiceError


def create_customer(
  deps: CustomerRouterDeps,
  *,
  customer_code: str,
  customer_name: str,
  account_manager_name: str,
  introducer_name: str,
  customer_level: int,
  special_notes: str,
) -> bool:
  if not customer_code or not customer_name:
    raise CustomerServiceError('客户编号和客户名称不能为空', 400)

  now = deps.now_str_func()
  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    insert_customer(
      cur,
      customer_id=str(uuid.uuid4()),
      customer_code=customer_code,
      customer_name=customer_name,
      account_manager_name=account_manager_name,
      introducer_name=introducer_name,
      customer_level=customer_level,
      special_notes=special_notes,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise CustomerServiceError('客户编号已存在', 400) from error

  conn.close()
  return True


def update_customer(
  deps: CustomerRouterDeps,
  *,
  customer_id: str,
  customer_code: str,
  customer_name: str,
  account_manager_name: str,
  introducer_name: str,
  customer_level: int,
  special_notes: str,
) -> bool:
  if not customer_id:
    raise CustomerServiceError('客户ID不能为空', 400)
  if not customer_code or not customer_name:
    raise CustomerServiceError('客户编号和客户名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_customer_id(cur, customer_id)
  if not row:
    conn.close()
    raise CustomerServiceError('客户不存在', 404)

  duplicate_row = fetch_customer_id_by_code_excluding_id(cur, customer_code, customer_id)
  if duplicate_row:
    conn.close()
    raise CustomerServiceError('客户编号已存在', 400)

  update_customer_row(
    cur,
    customer_id=customer_id,
    customer_code=customer_code,
    customer_name=customer_name,
    account_manager_name=account_manager_name,
    introducer_name=introducer_name,
    customer_level=customer_level,
    special_notes=special_notes,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def delete_customer(deps: CustomerRouterDeps, *, customer_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_customer_row(cur, customer_id)
  conn.commit()
  conn.close()
  return True
