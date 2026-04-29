from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.system_admin.deps import UserRouterDeps
from app.modules.system_admin.helpers import parse_user_create_payload, parse_user_update_payload
from app.modules.system_admin.services.errors import SystemAdminServiceError
from app.modules.system_admin.services.user_command_service import (
  create_user_record,
  delete_user_record,
  reset_user_password_record,
  update_user_base_info_record,
  update_user_enabled_record,
  update_user_password_record,
  update_user_record,
)
from app.modules.system_admin.services.user_query_service import (
  get_all_users,
  get_user_by_id_detail,
  get_user_info,
  query_user_page,
)


def register_user_routes(router: APIRouter, deps: UserRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/admin/user/info')
  def user_info(request: Request) -> Any:
    try:
      return ok_func(get_user_info(deps, request=request), 'success')
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)

  @router.get('/admin/user/getAllUser')
  def all_users() -> dict[str, Any]:
    return ok_func(get_all_users(deps), 'success')

  @router.get('/admin/user/page')
  def page_users(
    current: int = 1,
    size: int = 10,
    username: str | None = None,
    realName: str | None = None,
    roleId: str | None = None,
    enabled: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_user_page(
        deps,
        current=current,
        size=size,
        username=username,
        real_name=realName,
        role_id=roleId,
        enabled=enabled,
      ),
      'success',
    )

  @router.get('/admin/user/{user_id}')
  def user_detail(user_id: str) -> Any:
    try:
      return ok_func(get_user_by_id_detail(deps, user_id=user_id), 'success')
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/admin/user')
  async def save_user(request: Request) -> Any:
    payload = parse_user_create_payload(await request.json())
    try:
      create_user_record(
        deps,
        username=payload['username'],
        real_name=payload['real_name'],
        raw_password=payload['raw_password'],
        phone=payload['phone'],
        email=payload['email'],
        role_id=payload['role_id'],
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/admin/user')
  async def edit_user(request: Request) -> Any:
    payload = parse_user_update_payload(await request.json())
    try:
      update_user_record(
        deps,
        user_id=payload['user_id'],
        real_name=payload['real_name'],
        phone=payload['phone'],
        email=payload['email'],
        role_id=payload['role_id'],
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/admin/user/updatePwd')
  async def edit_user_password(request: Request) -> Any:
    payload = await request.json()
    try:
      update_user_password_record(
        deps,
        user_id=str(payload.get('userId', '')).strip(),
        raw_password=str(payload.get('password', '')).strip(),
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/admin/user/updateBaseInfo')
  async def edit_user_base_info(request: Request) -> Any:
    payload = await request.json()
    try:
      update_user_base_info_record(
        deps,
        user_id=str(payload.get('userId', '')).strip(),
        real_name=str(payload.get('realName', '')).strip(),
        phone=str(payload.get('phone', '')).strip(),
        email=str(payload.get('email', '')).strip(),
      )
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/admin/user/{user_id}')
  def remove_user(user_id: str) -> Any:
    try:
      delete_user_record(deps, user_id=user_id)
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/admin/user/resetPwd')
  @router.get('/admin/user/resetPwd/{id}')
  def reset_user_password(id: str | None = None) -> Any:
    try:
      reset_user_password_record(deps, user_id=id)
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/admin/user/enabled')
  def user_enabled(id: str, enabled: int | None = None, type: int | None = None) -> dict[str, Any]:
    enable_value = enabled if enabled is not None else type
    final_enabled = 1 if int(str(enable_value or 0)) == 1 else 0
    update_user_enabled_record(deps, user_id=id, enabled=final_enabled)
    return ok_func(True, 'success')
