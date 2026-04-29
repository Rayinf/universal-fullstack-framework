from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.system.deps import SystemConfigRouterDeps
from app.modules.system.helpers import normalize_system_config_payload
from app.modules.system.services.errors import SystemServiceError
from app.modules.system.services.system_config_command_service import (
  update_system_config_all as update_system_config_all_command,
  update_system_config_single as update_system_config_single_command,
)
from app.modules.system.services.system_config_query_service import (
  get_system_default_data,
  get_tenant_name,
)


def register_system_config_routes(router: APIRouter, deps: SystemConfigRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/manage/api/tenant/getTenantName')
  def tenant_name() -> dict[str, Any]:
    return ok_func(get_tenant_name(), 'success')

  @router.get('/manage/api/systemConfig/getSystemDefaultData')
  def system_default_data() -> dict[str, Any]:
    return ok_func(get_system_default_data(deps), 'success')

  @router.put('/manage/api/systemConfig/update')
  async def update_system_config_single(request: Request) -> Any:
    payload = await request.json()
    try:
      update_system_config_single_command(
        deps,
        code=str(payload.get('code', '')).strip(),
        value=str(payload.get('value', '')).strip(),
      )
    except SystemServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/systemConfig/updateSystemDefaultData')
  async def update_system_config_all(request: Request) -> dict[str, Any]:
    payload = normalize_system_config_payload(await request.json())
    update_system_config_all_command(
      deps,
      company_name=payload['companyName'],
      system_name=payload['systemName'],
      version=payload['version'],
    )
    return ok_func(True, 'success')
