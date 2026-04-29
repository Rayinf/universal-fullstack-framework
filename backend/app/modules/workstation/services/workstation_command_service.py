from __future__ import annotations

import uuid

from app.modules.workstation.deps import WorkstationRouterDeps
from app.modules.workstation.repositories.workstation_repo import (
  delete_devices_by_workstation,
  delete_workstation as delete_workstation_row,
  fetch_other_workstation_by_no,
  fetch_workstation_by_id,
  fetch_workstation_by_no,
  insert_workstation,
  update_workstation as update_workstation_row,
  update_workstation_status as update_workstation_status_row,
)
from app.modules.workstation.services.errors import WorkstationServiceError


def create_workstation(
  deps: WorkstationRouterDeps,
  *,
  workstation_no: int,
  workstation_name: str,
  workstation_type: int,
  status: int,
  responsible_person: str,
  dept_id: str,
  process_library_id: str,
  remarks: str,
) -> bool:
  if workstation_no <= 0 or not workstation_name:
    raise WorkstationServiceError('工位编号和工位名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if fetch_workstation_by_no(cur, workstation_no):
    conn.close()
    raise WorkstationServiceError('工位编号已存在', 400)

  insert_workstation(
    cur,
    workstation_id=str(uuid.uuid4()),
    workstation_no=workstation_no,
    workstation_name=workstation_name,
    workstation_type=workstation_type,
    status=status,
    responsible_person=responsible_person,
    dept_id=dept_id,
    process_library_id=process_library_id,
    remarks=remarks,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def update_workstation(
  deps: WorkstationRouterDeps,
  *,
  workstation_id: str,
  workstation_no: int,
  workstation_name: str,
  workstation_type: int,
  status: int,
  responsible_person: str,
  dept_id: str,
  process_library_id: str,
  remarks: str,
) -> bool:
  if not workstation_id:
    raise WorkstationServiceError('工位ID不能为空', 400)
  if workstation_no <= 0 or not workstation_name:
    raise WorkstationServiceError('工位编号和工位名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_workstation_by_id(cur, workstation_id):
    conn.close()
    raise WorkstationServiceError('工位不存在', 404)
  if fetch_other_workstation_by_no(cur, workstation_no, workstation_id):
    conn.close()
    raise WorkstationServiceError('工位编号已存在', 400)

  update_workstation_row(
    cur,
    workstation_id=workstation_id,
    workstation_no=workstation_no,
    workstation_name=workstation_name,
    workstation_type=workstation_type,
    status=status,
    responsible_person=responsible_person,
    dept_id=dept_id,
    process_library_id=process_library_id,
    remarks=remarks,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def delete_workstation(deps: WorkstationRouterDeps, *, workstation_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_devices_by_workstation(cur, workstation_id)
  delete_workstation_row(cur, workstation_id)
  conn.commit()
  conn.close()
  return True


def update_workstation_status(
  deps: WorkstationRouterDeps,
  *,
  workstation_id: str,
  status: int,
) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_workstation_status_row(cur, workstation_id, deps.safe_int_func(status, 1), deps.now_str_func())
  conn.commit()
  conn.close()
  return True
