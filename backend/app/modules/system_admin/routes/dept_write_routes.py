from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.system_admin.deps import DeptWriteRouterDeps
from app.modules.system_admin.helpers import parse_dept_payload
from app.modules.system_admin.services.dept_command_service import (
  create_dept,
  delete_dept,
  update_dept,
  update_dept_enabled,
  update_dept_users,
)
from app.modules.system_admin.services.errors import SystemAdminServiceError


def register_dept_write_routes(router: APIRouter, deps: DeptWriteRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func

  @router.post('/admin/dept')
  async def save_dept(request: Request) -> Any:
    payload = parse_dept_payload(await request.json(), safe_int_func)
    try:
      create_dept(
        deps,
        name=payload['name'],
        parent_id=payload['parent_id'],
        sort_order=payload['sort_order'],
        enabled=payload['enabled'],
        user_id_list=payload['user_id_list'],
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/admin/dept')
  async def edit_dept(request: Request) -> Any:
    payload = parse_dept_payload(await request.json(), safe_int_func)
    try:
      update_dept(
        deps,
        dept_id=payload['dept_id'],
        name=payload['name'],
        parent_id=payload['parent_id'],
        sort_order=payload['sort_order'],
        enabled=payload['enabled'],
        user_id_list=payload['user_id_list'],
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/admin/dept/{dept_id}')
  def remove_dept(dept_id: str) -> Any:
    try:
      delete_dept(deps, dept_id=dept_id)
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/admin/dept/enabled')
  def dept_enabled(id: str, type: int = 0) -> dict[str, Any]:
    update_dept_enabled(deps, dept_id=id, enabled=1 if safe_int_func(type, 0) == 1 else 0)
    return ok_func(True, 'success')

  @router.post('/admin/dept/updateUserDeptId')
  async def edit_dept_users(request: Request) -> Any:
    payload = await request.json()
    try:
      update_dept_users(
        deps,
        dept_id=str(payload.get('deptId', '')).strip(),
        user_id_list=payload.get('userIdList') or [],
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
