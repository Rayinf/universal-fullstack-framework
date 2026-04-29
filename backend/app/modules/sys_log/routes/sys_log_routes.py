from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.modules.sys_log.deps import SysLogRouterDeps
from app.modules.sys_log.helpers import normalize_id_list
from app.modules.sys_log.services.errors import SysLogServiceError
from app.modules.sys_log.services.sys_log_command_service import clear_sys_logs, delete_sys_logs
from app.modules.sys_log.services.sys_log_query_service import export_sys_logs, get_sys_log_detail, query_sys_log_page


def register_sys_log_routes(router: APIRouter, deps: SysLogRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/admin/api/sysLogUser')
  def page_sys_log_users(
    current: int = 1,
    size: int = 10,
    logType: int | None = None,
    content: str | None = None,
    realName: str | None = None,
    username: str | None = None,
    startTime: str | None = None,
    endTime: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_sys_log_page(
        deps,
        current=current,
        size=size,
        log_type=logType,
        content=content,
        real_name=realName,
        username=username,
        start_time=startTime,
        end_time=endTime,
      ),
      'success',
    )

  @router.delete('/admin/api/sysLogUser')
  def delete_sys_log_users(request: Request) -> Any:
    try:
      delete_sys_logs(deps, id_list=normalize_id_list(request.query_params.getlist('idList')))
    except SysLogServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/admin/api/sysLogUser/clearLog')
  def clear_sys_log_users(logType: int = 1, clearType: int = 9) -> dict[str, Any]:
    clear_sys_logs(deps, log_type=logType, clear_type=clearType)
    return ok_func(True, 'success')

  @router.post('/admin/api/sysLogUser/exportLog')
  def export_sys_log_users() -> Response:
    return Response(
      content=export_sys_logs(deps),
      media_type='text/csv',
      headers={'Content-Disposition': 'attachment; filename=operation-logs.csv'},
    )

  @router.get('/admin/api/sysLogUser/{log_id}')
  def get_sys_log_user_detail(log_id: int) -> Any:
    try:
      data = get_sys_log_detail(deps, log_id=log_id)
    except SysLogServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(data, 'success')
