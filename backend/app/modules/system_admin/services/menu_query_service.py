from __future__ import annotations

from app.modules.system_admin.deps import SystemAdminRouterDeps
from app.modules.system_admin.repositories.menu_repo import query_role_menu_rows


def get_menu_tree(deps: SystemAdminRouterDeps) -> list[dict[str, object]]:
  return deps.menu_tree_func()


def get_role_menu_ids(deps: SystemAdminRouterDeps, *, role_id: str) -> list[str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_role_menu_rows(cur, role_id)
  conn.close()
  return [str(row['menu_id']) for row in rows]
