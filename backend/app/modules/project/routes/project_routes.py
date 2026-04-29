from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.project.deps import ProjectRouterDeps
from app.modules.project.helpers import parse_project_payload
from app.modules.project.services.errors import ProjectServiceError
from app.modules.project.services.project_command_service import (
  create_project as create_project_command,
  delete_project as delete_project_command,
  update_project as update_project_command,
)
from app.modules.project.services.project_query_service import query_project_page


def register_project_routes(router: APIRouter, deps: ProjectRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func

  @router.get('/local/projects/page')
  def page_projects(current: int = 1, size: int = 10, keyword: str | None = None, status: int | None = None) -> dict[str, Any]:
    return ok_func(query_project_page(deps, current=current, size=size, keyword=keyword, status=status), 'success')

  @router.post('/local/projects')
  async def create_project(request: Request) -> Any:
    payload = parse_project_payload(await request.json(), safe_int_func)
    try:
      create_project_command(
        deps,
        project_code=payload['project_code'],
        project_name=payload['project_name'],
        owner_name=payload['owner_name'],
        priority=payload['priority'],
        project_status=payload['project_status'],
        progress=payload['progress'],
        start_date=payload['start_date'],
        end_date=payload['end_date'],
        remark=payload['remark'],
      )
    except ProjectServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/local/projects/{project_id}')
  async def update_project(project_id: str, request: Request) -> Any:
    payload = parse_project_payload(await request.json(), safe_int_func)
    try:
      update_project_command(
        deps,
        project_id=project_id,
        project_code=payload['project_code'],
        project_name=payload['project_name'],
        owner_name=payload['owner_name'],
        priority=payload['priority'],
        project_status=payload['project_status'],
        progress=payload['progress'],
        start_date=payload['start_date'],
        end_date=payload['end_date'],
        remark=payload['remark'],
      )
    except ProjectServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/projects/{project_id}')
  def delete_project(project_id: str) -> dict[str, Any]:
    delete_project_command(deps, project_id=project_id)
    return ok_func(True, 'success')
