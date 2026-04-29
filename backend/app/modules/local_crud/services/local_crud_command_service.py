from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.local_crud.deps import LocalCrudRouterDeps
from app.modules.local_crud.repositories.crud_item_repo import (
  delete_crud_item as delete_crud_item_row,
  fetch_crud_item_id,
  insert_crud_item,
  update_crud_item as update_crud_item_row,
)
from app.modules.local_crud.services.errors import LocalCrudServiceError


def create_crud_item(
  deps: LocalCrudRouterDeps,
  *,
  name: str,
  code: str,
  remark: str,
  status: int,
) -> bool:
  if not name or not code:
    raise LocalCrudServiceError('名称和编码不能为空', 400)

  now = deps.now_str_func()
  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    insert_crud_item(
      cur,
      item_id=str(uuid.uuid4()),
      name=name,
      code=code,
      remark=remark,
      status=status,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise LocalCrudServiceError('编码已存在', 400) from error

  conn.close()
  return True


def update_crud_item(
  deps: LocalCrudRouterDeps,
  *,
  item_id: str,
  name: str,
  code: str,
  remark: str,
  status: int,
) -> bool:
  if not name or not code:
    raise LocalCrudServiceError('名称和编码不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_crud_item_id(cur, item_id)
  if not row:
    conn.close()
    raise LocalCrudServiceError('记录不存在', 404)

  try:
    update_crud_item_row(
      cur,
      item_id=item_id,
      name=name,
      code=code,
      remark=remark,
      status=status,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise LocalCrudServiceError('编码已存在', 400) from error

  conn.close()
  return True


def delete_crud_item(deps: LocalCrudRouterDeps, *, item_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_crud_item_row(cur, item_id)
  conn.commit()
  conn.close()
  return True
