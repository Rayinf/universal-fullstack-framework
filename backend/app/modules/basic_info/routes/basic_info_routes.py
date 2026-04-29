from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.basic_info.deps import BasicInfoRouterDeps
from app.modules.basic_info.helpers import parse_basic_info_payload
from app.modules.basic_info.services.basic_info_command_service import (
  create_basic_info as create_basic_info_command,
  delete_basic_info as delete_basic_info_command,
  update_basic_info as update_basic_info_command,
)
from app.modules.basic_info.services.basic_info_query_service import (
  list_basic_info as list_basic_info_query,
  query_basic_info_page,
)
from app.modules.basic_info.services.errors import BasicInfoServiceError


def register_basic_info_routes(router: APIRouter, deps: BasicInfoRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/manage/api/basicInformation/page')
  def page_basic_information(
    page: int | None = None,
    current: int | None = None,
    size: int = 10,
    type: int | None = None,
    keyWord: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_basic_info_page(
        deps,
        page=page,
        current=current,
        size=size,
        info_type=type,
        key_word=keyWord,
      ),
      'success',
    )

  @router.get('/manage/api/basicInformation/list')
  def list_basic_information(type: int | None = None) -> dict[str, Any]:
    return ok_func(list_basic_info_query(deps, info_type=type), 'success')

  @router.post('/manage/api/basicInformation/save')
  async def save_basic_information(request: Request) -> Any:
    payload = parse_basic_info_payload(await request.json(), deps.safe_int_func)
    try:
      create_basic_info_command(
        deps,
        name=payload['name'],
        info_type=payload['type'],
        parent_id=payload['parent_id'],
      )
    except BasicInfoServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/basicInformation/update')
  async def update_basic_information(request: Request) -> Any:
    payload = parse_basic_info_payload(await request.json(), deps.safe_int_func)
    try:
      update_basic_info_command(
        deps,
        info_id=payload['id'],
        name=payload['name'],
        info_type=payload['type'],
        parent_id=payload['parent_id'],
      )
    except BasicInfoServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/manage/api/basicInformation/{info_id}')
  def delete_basic_information(info_id: int) -> dict[str, Any]:
    delete_basic_info_command(deps, info_id=info_id)
    return ok_func(True, 'success')
