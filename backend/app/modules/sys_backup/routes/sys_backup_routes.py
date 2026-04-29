from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.modules.sys_backup.deps import SysBackupRouterDeps
from app.modules.sys_backup.services.errors import SysBackupServiceError
from app.modules.sys_backup.services.sys_backup_command_service import (
  delete_sys_backup,
  recovery_sys_backup,
  save_sys_backup_config,
  trigger_sys_backup,
)
from app.modules.sys_backup.services.sys_backup_query_service import (
  get_sys_backup_config,
  get_sys_backup_download,
  query_sys_backup_page,
)


def register_sys_backup_routes(router: APIRouter, deps: SysBackupRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/manage/api/sysBakInfo/page')
  def page_sys_backup_infos(
    current: int = 1,
    size: int = 10,
    name: str | None = None,
    type: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_sys_backup_page(deps, current=current, size=size, name=name, type_code=type),
      'success',
    )

  @router.get('/manage/api/sysBakInfo/backup')
  def backup_sys_backup(verificationCode: str | None = None) -> Any:
    try:
      trigger_sys_backup(deps, verification_code=verificationCode)
    except SysBackupServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/manage/api/sysBakInfo/del')
  def delete_sys_backup_route(id: str, verificationCode: str | None = None) -> Any:
    try:
      delete_sys_backup(deps, backup_id=id, verification_code=verificationCode)
    except SysBackupServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/manage/api/sysBakInfo/download/{backup_id}')
  def download_sys_backup(backup_id: str) -> Any:
    try:
      result = get_sys_backup_download(deps, backup_id=backup_id)
    except SysBackupServiceError as error:
      return fail_func(error.message, error.code)
    return Response(
      content=result['file_content'].encode('utf-8'),
      media_type='application/octet-stream',
      headers={'Content-Disposition': f'attachment; filename="{result["name"]}"'},
    )

  @router.get('/manage/api/sysBakInfo/recovery')
  def recovery_sys_backup_route(id: str | None = None) -> dict[str, Any]:
    return ok_func(recovery_sys_backup(backup_id=id), 'success')

  @router.post('/manage/api/sysBakInfo/getSysBakConfigInfo')
  def get_sys_backup_config_info() -> dict[str, Any]:
    return ok_func(get_sys_backup_config(deps), 'success')

  @router.post('/manage/api/sysBakInfo/saveScheduledTask')
  async def save_sys_backup_config_route(request: Request) -> dict[str, Any]:
    save_sys_backup_config(deps, payload=await request.json())
    return ok_func(True, 'success')
