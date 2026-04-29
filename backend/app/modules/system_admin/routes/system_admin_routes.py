from __future__ import annotations

from fastapi import APIRouter

from app.modules.system_admin.deps import SystemAdminRouterDeps
from app.modules.system_admin.services.menu_query_service import get_menu_tree, get_role_menu_ids


def register_system_admin_routes(router: APIRouter, deps: SystemAdminRouterDeps) -> None:
  ok_func = deps.ok_func

  @router.get('/admin/menu/tree')
  def menu_tree() -> dict[str, object]:
    return ok_func(get_menu_tree(deps), 'success')

  @router.get('/admin/menu/tree/{role_id}')
  def role_menu_ids(role_id: str) -> dict[str, object]:
    return ok_func(get_role_menu_ids(deps, role_id=role_id), 'success')
