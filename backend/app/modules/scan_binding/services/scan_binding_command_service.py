from __future__ import annotations

from app.modules.scan_binding.deps import ScanBindingRouterDeps
from app.modules.scan_binding.repositories.scan_binding_repo import (
  delete_scan_binding_process as delete_scan_binding_process_row,
  fetch_scan_binding_by_id,
  insert_scan_binding_process,
  update_scan_binding_process as update_scan_binding_process_row,
)
from app.modules.scan_binding.services.errors import ScanBindingServiceError


def create_scan_binding_process(
  deps: ScanBindingRouterDeps,
  *,
  scan_asset_number: str,
  identifier: str,
  process_id: int,
) -> bool:
  if not scan_asset_number or not identifier or process_id <= 0:
    raise ScanBindingServiceError('参数不完整', 400)

  now = deps.now_str_func()
  conn = deps.get_conn_func()
  cur = conn.cursor()
  insert_scan_binding_process(
    cur,
    scan_asset_number=scan_asset_number,
    identifier=identifier,
    process_id=process_id,
    now=now,
  )
  conn.commit()
  conn.close()
  return True


def update_scan_binding_process(
  deps: ScanBindingRouterDeps,
  *,
  record_id: int,
  scan_asset_number: str,
  identifier: str,
  process_id: int,
) -> bool:
  if record_id <= 0 or not scan_asset_number or not identifier or process_id <= 0:
    raise ScanBindingServiceError('参数不完整', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_scan_binding_by_id(cur, record_id):
    conn.close()
    raise ScanBindingServiceError('记录不存在', 404)
  update_scan_binding_process_row(
    cur,
    record_id=record_id,
    scan_asset_number=scan_asset_number,
    identifier=identifier,
    process_id=process_id,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def delete_scan_binding_process(deps: ScanBindingRouterDeps, *, record_id: int) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_scan_binding_process_row(cur, record_id)
  conn.commit()
  conn.close()
  return True
