from __future__ import annotations

from app.modules.basic_info.deps import BasicInfoRouterDeps
from app.modules.basic_info.repositories.basic_info_repo import (
  delete_basic_info as delete_basic_info_row,
  fetch_basic_info_by_id,
  fetch_basic_info_by_type_and_name,
  fetch_other_basic_info_by_type_and_name,
  insert_basic_info,
  update_basic_info as update_basic_info_row,
)
from app.modules.basic_info.services.errors import BasicInfoServiceError


def create_basic_info(
  deps: BasicInfoRouterDeps,
  *,
  name: str,
  info_type: int,
  parent_id: object,
) -> bool:
  if not name or info_type <= 0:
    raise BasicInfoServiceError('名称和类型不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if fetch_basic_info_by_type_and_name(cur, info_type, name):
    conn.close()
    raise BasicInfoServiceError('同类型下名称已存在', 400)

  insert_basic_info(
    cur,
    name=name,
    info_type=info_type,
    parent_id=deps.safe_int_func(parent_id) if parent_id is not None else None,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def update_basic_info(
  deps: BasicInfoRouterDeps,
  *,
  info_id: int,
  name: str,
  info_type: int,
  parent_id: object,
) -> bool:
  if info_id <= 0 or not name or info_type <= 0:
    raise BasicInfoServiceError('参数不完整', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_basic_info_by_id(cur, info_id):
    conn.close()
    raise BasicInfoServiceError('记录不存在', 404)
  if fetch_other_basic_info_by_type_and_name(cur, info_type, name, info_id):
    conn.close()
    raise BasicInfoServiceError('同类型下名称已存在', 400)

  update_basic_info_row(
    cur,
    info_id=info_id,
    name=name,
    info_type=info_type,
    parent_id=deps.safe_int_func(parent_id) if parent_id is not None else None,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def delete_basic_info(deps: BasicInfoRouterDeps, *, info_id: int) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_basic_info_row(cur, int(info_id))
  conn.commit()
  conn.close()
  return True
