from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.project.deps import ProjectRouterDeps
from app.modules.project.helpers import clamp_progress
from app.modules.project.repositories.project_repo import (
  delete_project as delete_project_row,
  fetch_project_id,
  insert_project,
  update_project as update_project_row,
)
from app.modules.project.services.errors import ProjectServiceError


def create_project(
  deps: ProjectRouterDeps,
  *,
  project_code: str,
  project_name: str,
  owner_name: str,
  priority: int,
  project_status: int,
  progress: int,
  start_date: str,
  end_date: str,
  remark: str,
) -> bool:
  if not project_code or not project_name:
    raise ProjectServiceError('项目编码和项目名称不能为空', 400)

  now = deps.now_str_func()
  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    insert_project(
      cur,
      project_id=str(uuid.uuid4()),
      project_code=project_code,
      project_name=project_name,
      owner_name=owner_name,
      priority=priority,
      project_status=project_status,
      progress=clamp_progress(progress),
      start_date=start_date,
      end_date=end_date,
      remark=remark,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ProjectServiceError('项目编码已存在', 400) from error

  conn.close()
  return True


def update_project(
  deps: ProjectRouterDeps,
  *,
  project_id: str,
  project_code: str,
  project_name: str,
  owner_name: str,
  priority: int,
  project_status: int,
  progress: int,
  start_date: str,
  end_date: str,
  remark: str,
) -> bool:
  if not project_code or not project_name:
    raise ProjectServiceError('项目编码和项目名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_project_id(cur, project_id)
  if not row:
    conn.close()
    raise ProjectServiceError('项目不存在', 404)

  try:
    update_project_row(
      cur,
      project_id=project_id,
      project_code=project_code,
      project_name=project_name,
      owner_name=owner_name,
      priority=priority,
      project_status=project_status,
      progress=clamp_progress(progress),
      start_date=start_date,
      end_date=end_date,
      remark=remark,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ProjectServiceError('项目编码已存在', 400) from error

  conn.close()
  return True


def delete_project(deps: ProjectRouterDeps, *, project_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_project_row(cur, project_id)
  conn.commit()
  conn.close()
  return True
