from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.system_admin.deps import RoleRouterDeps
from app.modules.system_admin.helpers import parse_role_menu_payload, parse_role_payload
from app.modules.system_admin.services.errors import SystemAdminServiceError
from app.modules.system_admin.services.role_command_service import (
  create_role_record,
  delete_role_record,
  update_role_menu_record,
  update_role_record,
)
from app.modules.system_admin.services.role_query_service import (
  get_role_by_id_detail,
  list_roles,
  list_user_ids_by_role,
  query_role_page,
)


def register_role_routes(router: APIRouter, deps: RoleRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/admin/role/list')
  def role_list() -> dict[str, Any]:
    return ok_func(list_roles(deps), 'success')

  @router.get('/admin/role/page')
  def page_roles(current: int = 1, size: int = 10, roleName: str | None = None) -> dict[str, Any]:
    return ok_func(query_role_page(deps, current=current, size=size, role_name=roleName), 'success')

  @router.get('/admin/role/{role_id}')
  def role_detail(role_id: str) -> Any:
    try:
      return ok_func(get_role_by_id_detail(deps, role_id=role_id), 'success')
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/admin/role')
  async def save_role(request: Request) -> Any:
    payload = parse_role_payload(await request.json())
    try:
      create_role_record(
        deps,
        role_name=payload['role_name'],
        role_code=payload['role_code'],
        role_desc=payload['role_desc'],
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/admin/role')
  async def edit_role(request: Request) -> Any:
    payload = parse_role_payload(await request.json())
    try:
      update_role_record(
        deps,
        role_id=payload['role_id'],
        role_name=payload['role_name'],
        role_code=payload['role_code'],
        role_desc=payload['role_desc'],
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/admin/role/{role_id}')
  def remove_role(role_id: str) -> Any:
    try:
      delete_role_record(deps, role_id=role_id)
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/admin/role/menu')
  async def edit_role_menu(request: Request) -> Any:
    payload = parse_role_menu_payload(await request.json())
    try:
      update_role_menu_record(deps, role_id=payload['role_id'], menu_ids=payload['menu_ids'])
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/admin/role/getUserByRoleId')
  def role_user_ids(roleId: str) -> dict[str, Any]:
    return ok_func(list_user_ids_by_role(deps, role_id=roleId), 'success')

  @router.get('/admin/role/export')
  def export_role() -> dict[str, Any]:
    return ok_func([], 'success')
