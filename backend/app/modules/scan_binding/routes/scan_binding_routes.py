from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.scan_binding.deps import ScanBindingRouterDeps
from app.modules.scan_binding.helpers import parse_scan_binding_payload
from app.modules.scan_binding.services.errors import ScanBindingServiceError
from app.modules.scan_binding.services.scan_binding_command_service import (
  create_scan_binding_process as create_scan_binding_process_command,
  delete_scan_binding_process as delete_scan_binding_process_command,
  update_scan_binding_process as update_scan_binding_process_command,
)
from app.modules.scan_binding.services.scan_binding_query_service import query_scan_binding_page


def register_scan_binding_routes(router: APIRouter, deps: ScanBindingRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/manage/api/scanBindingProcess/page')
  def page_scan_binding_process(
    page: int | None = None,
    current: int | None = None,
    size: int = 10,
    keyWord: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_scan_binding_page(
        deps,
        page=page,
        current=current,
        size=size,
        keyword=keyWord,
      ),
      'success',
    )

  @router.post('/manage/api/scanBindingProcess/save')
  async def save_scan_binding_process(request: Request) -> Any:
    payload = parse_scan_binding_payload(await request.json(), deps.safe_int_func)
    try:
      create_scan_binding_process_command(
        deps,
        scan_asset_number=payload['scan_asset_number'],
        identifier=payload['identifier'],
        process_id=payload['process_id'],
      )
    except ScanBindingServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/scanBindingProcess/update')
  async def update_scan_binding_process(request: Request) -> Any:
    payload = parse_scan_binding_payload(await request.json(), deps.safe_int_func)
    try:
      update_scan_binding_process_command(
        deps,
        record_id=payload['record_id'],
        scan_asset_number=payload['scan_asset_number'],
        identifier=payload['identifier'],
        process_id=payload['process_id'],
      )
    except ScanBindingServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/manage/api/scanBindingProcess/{record_id}')
  def delete_scan_binding_process(record_id: int) -> dict[str, Any]:
    delete_scan_binding_process_command(deps, record_id=record_id)
    return ok_func(True, 'success')
