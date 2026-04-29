from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.device.deps import DeviceRouterDeps
from app.modules.device.helpers import parse_device_payload
from app.modules.device.services.device_command_service import (
  create_device as create_device_command,
  delete_device as delete_device_command,
  update_device as update_device_command,
  update_device_status as update_device_status_command,
)
from app.modules.device.services.device_query_service import (
  get_device_detail as get_device_detail_query,
  list_devices as list_devices_query,
  query_device_page,
)
from app.modules.device.services.errors import DeviceServiceError


def register_device_routes(router: APIRouter, deps: DeviceRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func

  @router.get('/manage/api/deviceInfo/page')
  def page_devices(
    page: int | None = None,
    current: int | None = None,
    size: int = 10,
    keyWord: str | None = None,
    deviceCategoryId: str | None = None,
    status: int | None = None,
    workstationId: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_device_page(
        deps,
        page=page,
        current=current,
        size=size,
        keyword=keyWord,
        device_category_id=deviceCategoryId,
        status=status,
        workstation_id=workstationId,
      ),
      'success',
    )

  @router.get('/manage/api/deviceInfo/list')
  def list_devices() -> dict[str, Any]:
    return ok_func(list_devices_query(deps), 'success')

  @router.get('/manage/api/deviceInfo/getDetail/{device_id}')
  def get_device_detail(device_id: str) -> Any:
    try:
      return ok_func(get_device_detail_query(deps, device_id=device_id), 'success')
    except DeviceServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/manage/api/deviceInfo/save')
  async def save_device(request: Request) -> Any:
    payload = parse_device_payload(await request.json(), safe_int_func)
    try:
      create_device_command(
        deps,
        device_name=payload['device_name'],
        device_number=payload['device_number'],
        model=payload['model'],
        device_category_id=payload['device_category_id'],
        workstation_id=payload['workstation_id'],
        responsible_person=payload['responsible_person'],
        status=payload['status'],
        remarks=payload['remarks'],
        scrap_reason=payload['scrap_reason'],
      )
    except DeviceServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/deviceInfo/update')
  async def update_device(request: Request) -> Any:
    payload = parse_device_payload(await request.json(), safe_int_func)
    try:
      update_device_command(
        deps,
        device_id=payload['device_id'],
        device_name=payload['device_name'],
        device_number=payload['device_number'],
        model=payload['model'],
        device_category_id=payload['device_category_id'],
        workstation_id=payload['workstation_id'],
        responsible_person=payload['responsible_person'],
        status=payload['status'],
        remarks=payload['remarks'],
        scrap_reason=payload['scrap_reason'],
      )
    except DeviceServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/manage/api/deviceInfo/delete/{device_id}')
  def delete_device(device_id: str) -> dict[str, Any]:
    delete_device_command(deps, device_id=device_id)
    return ok_func(True, 'success')

  @router.get('/manage/api/deviceInfo/enable')
  def enable_device(id: str, status: int, scrapReason: str | None = None) -> dict[str, Any]:
    update_device_status_command(deps, device_id=id, status=status, scrap_reason=scrapReason)
    return ok_func(True, 'success')
