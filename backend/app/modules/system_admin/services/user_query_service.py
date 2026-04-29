from __future__ import annotations

from typing import Any

from fastapi import Request

from app.modules.system_admin.deps import UserRouterDeps
from app.modules.system_admin.repositories.user_repo import (
  fetch_dept_name,
  fetch_user_detail_row,
  query_all_user_brief_rows,
  query_user_page_rows,
  query_user_page_total,
)
from app.modules.system_admin.serializers import (
  build_page_result,
  user_brief_to_dict,
  user_detail_to_dict,
  user_info_to_dict,
  user_list_row_to_dict,
)
from app.modules.system_admin.services.errors import SystemAdminServiceError


def get_user_info(deps: UserRouterDeps, *, request: Request) -> dict[str, Any]:
  user = deps.get_current_user_func(request)
  if not user:
    raise SystemAdminServiceError('未找到用户', 401)

  dept_name = '本地组织'
  conn = deps.get_conn_func()
  cur = conn.cursor()
  dept_row = fetch_dept_name(cur, str(user['dept_id'] or '1'))
  conn.close()
  if dept_row and dept_row['name']:
    dept_name = dept_row['name']
  return user_info_to_dict(user, dept_name)


def get_all_users(deps: UserRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_all_user_brief_rows(cur)
  conn.close()
  return [user_brief_to_dict(row) for row in rows]


def query_user_page(
  deps: UserRouterDeps,
  *,
  current: int,
  size: int,
  username: str | None,
  real_name: str | None,
  role_id: str | None,
  enabled: int | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if username:
    where_sql += ' AND username LIKE ?'
    values.append(f'%{username.strip()}%')
  if real_name:
    where_sql += ' AND real_name LIKE ?'
    values.append(f'%{real_name.strip()}%')
  if role_id:
    where_sql += ' AND role_id = ?'
    values.append(str(role_id))
  if enabled is not None:
    where_sql += ' AND enabled = ?'
    values.append(int(enabled))

  page_current = max(current, 1)
  page_size = max(size, 1)
  total = int(query_user_page_total(cur, where_sql, values)['cnt'])
  rows = query_user_page_rows(cur, where_sql, values, page_size, (page_current - 1) * page_size)
  conn.close()
  return build_page_result([user_list_row_to_dict(row) for row in rows], total, page_current, page_size)


def get_user_by_id_detail(deps: UserRouterDeps, *, user_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_user_detail_row(cur, user_id)
  conn.close()
  if not row:
    raise SystemAdminServiceError('用户不存在', 404)
  return user_detail_to_dict(row)
