from __future__ import annotations

import uuid
from typing import Any

from app.modules.system_admin.deps import DeptWriteRouterDeps
from app.modules.system_admin.repositories.dept_repo import (
  assign_users_to_dept,
  delete_dept as delete_dept_record,
  fetch_dept_by_id,
  fetch_dept_by_name,
  fetch_other_dept_by_name,
  fetch_parent_dept,
  insert_dept,
  query_all_dept_rows,
  query_child_dept_count,
  query_dept_user_rows,
  reset_dept_users,
  update_dept as update_dept_record,
  update_dept_enabled as update_dept_enabled_record,
)
from app.modules.system_admin.services.errors import SystemAdminServiceError


def create_dept(
  deps: DeptWriteRouterDeps,
  *,
  name: str,
  parent_id: str,
  sort_order: int,
  enabled: int,
  user_id_list: list[Any],
) -> None:
  if not name:
    raise SystemAdminServiceError('部门名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if parent_id != '0':
    if not fetch_parent_dept(cur, parent_id):
      conn.close()
      raise SystemAdminServiceError('上级部门不存在', 400)

  if fetch_dept_by_name(cur, name):
    conn.close()
    raise SystemAdminServiceError('部门名称已存在', 400)

  now = deps.now_str_func()
  dept_id = str(uuid.uuid4())
  insert_dept(
    cur,
    dept_id=dept_id,
    name=name,
    parent_id=parent_id,
    sort_order=sort_order,
    enabled=enabled,
    now=now,
  )
  if user_id_list:
    assign_users_to_dept(cur, dept_id, now, user_id_list)
  conn.commit()
  conn.close()


def update_dept(
  deps: DeptWriteRouterDeps,
  *,
  dept_id: str,
  name: str,
  parent_id: str,
  sort_order: int,
  enabled: int,
  user_id_list: list[Any],
) -> None:
  if not dept_id:
    raise SystemAdminServiceError('deptId不能为空', 400)
  if not name:
    raise SystemAdminServiceError('部门名称不能为空', 400)
  if parent_id == dept_id:
    raise SystemAdminServiceError('上级部门不能是自己', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_dept_by_id(cur, dept_id):
    conn.close()
    raise SystemAdminServiceError('部门不存在', 404)

  all_dept_rows = query_all_dept_rows(cur)
  descendant_ids = deps.collect_descendant_ids_func(dept_id, all_dept_rows)
  if parent_id in descendant_ids:
    conn.close()
    raise SystemAdminServiceError('上级部门不能是当前部门的下级', 400)

  if parent_id != '0':
    if not fetch_parent_dept(cur, parent_id):
      conn.close()
      raise SystemAdminServiceError('上级部门不存在', 400)

  if fetch_other_dept_by_name(cur, name, dept_id):
    conn.close()
    raise SystemAdminServiceError('部门名称已存在', 400)

  now = deps.now_str_func()
  update_dept_record(
    cur,
    dept_id=dept_id,
    name=name,
    parent_id=parent_id,
    sort_order=sort_order,
    enabled=enabled,
    now=now,
  )
  reset_dept_users(cur, dept_id, now)
  if user_id_list:
    assign_users_to_dept(cur, dept_id, now, user_id_list)
  conn.commit()
  conn.close()


def delete_dept(deps: DeptWriteRouterDeps, *, dept_id: str) -> None:
  if dept_id == '1':
    raise SystemAdminServiceError('默认根部门不可删除', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_dept_by_id(cur, dept_id):
    conn.close()
    raise SystemAdminServiceError('部门不存在', 404)

  child_count = int(query_child_dept_count(cur, dept_id)['cnt'])
  user_count = len(query_dept_user_rows(cur, dept_id))
  if child_count > 0 or user_count > 0:
    conn.close()
    raise SystemAdminServiceError('请先移除子组织和成员后再删除', 400)

  delete_dept_record(cur, dept_id)
  conn.commit()
  conn.close()


def update_dept_enabled(deps: DeptWriteRouterDeps, *, dept_id: str, enabled: int) -> None:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_dept_enabled_record(cur, dept_id, enabled, deps.now_str_func())
  conn.commit()
  conn.close()


def update_dept_users(deps: DeptWriteRouterDeps, *, dept_id: str, user_id_list: Any) -> None:
  if not dept_id:
    raise SystemAdminServiceError('deptId不能为空', 400)
  if not isinstance(user_id_list, list):
    raise SystemAdminServiceError('userIdList格式错误', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_dept_by_id(cur, dept_id):
    conn.close()
    raise SystemAdminServiceError('部门不存在', 404)

  now = deps.now_str_func()
  reset_dept_users(cur, dept_id, now)
  if user_id_list:
    assign_users_to_dept(cur, dept_id, now, user_id_list)
  conn.commit()
  conn.close()
