from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.workstation.deps import WorkstationRouterDeps
from app.modules.workstation.helpers import parse_workstation_payload
from app.modules.workstation.services.errors import WorkstationServiceError
from app.modules.workstation.services.workstation_command_service import (
  create_workstation as create_workstation_command,
  delete_workstation as delete_workstation_command,
  update_workstation as update_workstation_command,
  update_workstation_status as update_workstation_status_command,
)
from app.modules.workstation.services.workstation_query_service import (
  get_workstation_detail as get_workstation_detail_query,
  list_workstations as list_workstations_query,
  query_workstation_page,
)


def register_workstation_routes(router: APIRouter, deps: WorkstationRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func

  @router.get('/manage/api/workstation/page')
  def page_workstations(
    page: int | None = None,
    current: int | None = None,
    size: int = 10,
    keywords: str | None = None,
    workstationName: str | None = None,
    workstationType: int | None = None,
    status: int | None = None,
    deptId: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_workstation_page(
        deps,
        page=page,
        current=current,
        size=size,
        keywords=keywords,
        workstation_name=workstationName,
        workstation_type=workstationType,
        status=status,
        dept_id=deptId,
      ),
      'success',
    )

  @router.get('/manage/api/workstation/list')
  def list_workstations() -> dict[str, Any]:
    return ok_func(list_workstations_query(deps), 'success')

  @router.get('/manage/api/workstation/{workstation_id}')
  def get_workstation_detail(workstation_id: str) -> Any:
    try:
      return ok_func(get_workstation_detail_query(deps, workstation_id=workstation_id), 'success')
    except WorkstationServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/manage/api/workstation/save')
  async def save_workstation(request: Request) -> Any:
    payload = parse_workstation_payload(await request.json(), safe_int_func)
    try:
      create_workstation_command(
        deps,
        workstation_no=payload['workstation_no'],
        workstation_name=payload['workstation_name'],
        workstation_type=payload['workstation_type'],
        status=payload['status'],
        responsible_person=payload['responsible_person'],
        dept_id=payload['dept_id'],
        process_library_id=payload['process_library_id'],
        remarks=payload['remarks'],
      )
    except WorkstationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/workstation/update')
  async def update_workstation(request: Request) -> Any:
    payload = parse_workstation_payload(await request.json(), safe_int_func)
    try:
      update_workstation_command(
        deps,
        workstation_id=payload['id'],
        workstation_no=payload['workstation_no'],
        workstation_name=payload['workstation_name'],
        workstation_type=payload['workstation_type'],
        status=payload['status'],
        responsible_person=payload['responsible_person'],
        dept_id=payload['dept_id'],
        process_library_id=payload['process_library_id'],
        remarks=payload['remarks'],
      )
    except WorkstationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/manage/api/workstation/{workstation_id}')
  def delete_workstation(workstation_id: str) -> dict[str, Any]:
    delete_workstation_command(deps, workstation_id=workstation_id)
    return ok_func(True, 'success')

  @router.get('/manage/api/workstation/status/{workstation_id}')
  def update_workstation_status(workstation_id: str, status: int = 1) -> dict[str, Any]:
    update_workstation_status_command(deps, workstation_id=workstation_id, status=status)
    return ok_func(True, 'success')
