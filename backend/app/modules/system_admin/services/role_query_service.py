from __future__ import annotations

from typing import Any

from app.modules.system_admin.deps import RoleRouterDeps
from app.modules.system_admin.repositories.role_repo import (
  fetch_role_by_id,
  query_role_list_rows,
  query_role_page_rows,
  query_role_page_total,
  query_user_ids_by_role,
)
from app.modules.system_admin.serializers import build_page_result, role_to_dict
from app.modules.system_admin.services.errors import SystemAdminServiceError


def list_roles(deps: RoleRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_role_list_rows(cur)
  conn.close()
  return [role_to_dict(row) for row in rows]


def query_role_page(deps: RoleRouterDeps, *, current: int, size: int, role_name: str | None) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if role_name and role_name.strip():
    where_sql += ' AND role_name LIKE ?'
    values.append(f'%{role_name.strip()}%')

  page_current = max(current, 1)
  page_size = max(size, 1)
  total = int(query_role_page_total(cur, where_sql, values)['cnt'])
  rows = query_role_page_rows(cur, where_sql, values, page_size, (page_current - 1) * page_size)
  conn.close()
  return build_page_result([role_to_dict(row) for row in rows], total, page_current, page_size)


def get_role_by_id_detail(deps: RoleRouterDeps, *, role_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_role_by_id(cur, role_id)
  conn.close()
  if not row:
    raise SystemAdminServiceError('角色不存在', 404)
  return role_to_dict(row)


def list_user_ids_by_role(deps: RoleRouterDeps, *, role_id: str) -> list[str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_user_ids_by_role(cur, role_id)
  conn.close()
  return [str(row['user_id']) for row in rows]
