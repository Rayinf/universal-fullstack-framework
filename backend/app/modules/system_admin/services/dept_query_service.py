from __future__ import annotations

from typing import Any

from app.modules.system_admin.deps import DeptReadRouterDeps
from app.modules.system_admin.repositories.dept_repo import (
  fetch_dept_by_id,
  fetch_dept_by_name,
  query_child_dept_count,
  query_dept_name_rows,
  query_dept_page_rows,
  query_dept_page_total,
  query_dept_user_rows,
)
from app.modules.system_admin.serializers import (
  build_page_result,
  dept_detail_to_dict,
  dept_detail_user_to_dict,
  dept_page_row_to_dict,
  dept_row_to_dict,
)
from app.modules.system_admin.services.errors import SystemAdminServiceError


def get_dept_tree(deps: DeptReadRouterDeps, *, include_users: bool = True) -> list[dict[str, Any]]:
  return deps.build_dept_tree_func(include_users=include_users)


def query_dept_page(
  deps: DeptReadRouterDeps,
  *,
  current: int,
  size: int,
  name: str,
  parent_id: str,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if name:
    where_sql += ' AND name LIKE ?'
    values.append(f'%{name}%')
  if parent_id:
    where_sql += ' AND parent_id = ?'
    values.append(parent_id)

  total = int(query_dept_page_total(cur, where_sql, values)['cnt'])
  page_size = max(size, 1)
  page_current = max(current, 1)
  offset = (page_current - 1) * page_size
  rows = query_dept_page_rows(cur, where_sql, values, page_size, offset)
  dept_name_rows = query_dept_name_rows(cur)
  conn.close()

  dept_name_map = {str(row['dept_id']): row['name'] for row in dept_name_rows}
  return build_page_result(
    [dept_page_row_to_dict(row, dept_name_map) for row in rows],
    total,
    page_current,
    page_size,
  )


def get_dept_by_name_detail(deps: DeptReadRouterDeps, *, dept_name: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_dept_by_name(cur, dept_name)
  conn.close()
  if not row:
    raise SystemAdminServiceError('部门不存在', 404)
  return dept_row_to_dict(row)


def get_dept_by_id_detail(deps: DeptReadRouterDeps, *, dept_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  dept_row = fetch_dept_by_id(cur, dept_id)
  if not dept_row:
    conn.close()
    raise SystemAdminServiceError('部门不存在', 404)

  all_depts = query_dept_name_rows(cur)
  child_dept_count = int(query_child_dept_count(cur, dept_id)['cnt'])
  user_rows = query_dept_user_rows(cur, dept_id)
  conn.close()

  dept_name_map = {str(row['dept_id']): row['name'] for row in all_depts}
  user_list = [dept_detail_user_to_dict(row) for row in user_rows]
  return dept_detail_to_dict(dept_row, dept_name_map, child_dept_count, user_list)
