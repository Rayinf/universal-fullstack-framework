from __future__ import annotations

import uuid

from app.modules.device.deps import DeviceRouterDeps
from app.modules.device.repositories.device_repo import (
  delete_device as delete_device_row,
  fetch_device_by_id,
  fetch_device_by_number,
  fetch_other_device_by_number,
  insert_device,
  update_device as update_device_row,
  update_device_status as update_device_status_row,
)
from app.modules.device.services.errors import DeviceServiceError


def create_device(
  deps: DeviceRouterDeps,
  *,
  device_name: str,
  device_number: str,
  model: str,
  device_category_id: str,
  workstation_id: str,
  responsible_person: str,
  status: int,
  remarks: str,
  scrap_reason: str,
) -> bool:
  if not device_name or not device_number or not model:
    raise DeviceServiceError('设备名称、设备编号、设备型号不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if fetch_device_by_number(cur, device_number):
    conn.close()
    raise DeviceServiceError('设备编号已存在', 400)

  insert_device(
    cur,
    device_id=str(uuid.uuid4()),
    device_name=device_name,
    device_number=device_number,
    model=model,
    device_category_id=device_category_id,
    workstation_id=workstation_id,
    responsible_person=responsible_person,
    status=status,
    remarks=remarks,
    scrap_reason=scrap_reason if status == 3 else '',
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def update_device(
  deps: DeviceRouterDeps,
  *,
  device_id: str,
  device_name: str,
  device_number: str,
  model: str,
  device_category_id: str,
  workstation_id: str,
  responsible_person: str,
  status: int,
  remarks: str,
  scrap_reason: str,
) -> bool:
  if not device_id:
    raise DeviceServiceError('设备ID不能为空', 400)
  if not device_name or not device_number or not model:
    raise DeviceServiceError('设备名称、设备编号、设备型号不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_device_by_id(cur, device_id):
    conn.close()
    raise DeviceServiceError('设备不存在', 404)
  if fetch_other_device_by_number(cur, device_number, device_id):
    conn.close()
    raise DeviceServiceError('设备编号已存在', 400)

  update_device_row(
    cur,
    device_id=device_id,
    device_name=device_name,
    device_number=device_number,
    model=model,
    device_category_id=device_category_id,
    workstation_id=workstation_id,
    responsible_person=responsible_person,
    status=status,
    remarks=remarks,
    scrap_reason=scrap_reason if status == 3 else '',
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def delete_device(deps: DeviceRouterDeps, *, device_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_device_row(cur, device_id)
  conn.commit()
  conn.close()
  return True


def update_device_status(
  deps: DeviceRouterDeps,
  *,
  device_id: str,
  status: int,
  scrap_reason: str | None,
) -> bool:
  new_status = deps.safe_int_func(status, 1)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_device_status_row(
    cur,
    device_id=device_id,
    status=new_status,
    scrap_reason=scrap_reason.strip() if (new_status == 3 and scrap_reason) else '',
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True
