from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.local_crud.deps import LocalCrudRouterDeps
from app.modules.local_crud.helpers import parse_crud_payload
from app.modules.local_crud.services.errors import LocalCrudServiceError
from app.modules.local_crud.services.local_crud_command_service import (
  create_crud_item as create_crud_item_command,
  delete_crud_item as delete_crud_item_command,
  update_crud_item as update_crud_item_command,
)
from app.modules.local_crud.services.local_crud_query_service import query_crud_item_page


def register_local_crud_routes(router: APIRouter, deps: LocalCrudRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/local/crud/page')
  def page_crud_items(current: int = 1, size: int = 10, keyword: str | None = None) -> dict[str, Any]:
    return ok_func(query_crud_item_page(deps, current=current, size=size, keyword=keyword), 'success')

  @router.post('/local/crud')
  async def create_crud_item(request: Request) -> Any:
    payload = parse_crud_payload(await request.json())
    try:
      create_crud_item_command(
        deps,
        name=payload['name'],
        code=payload['code'],
        remark=payload['remark'],
        status=payload['status'],
      )
    except LocalCrudServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/local/crud/{item_id}')
  async def update_crud_item(item_id: str, request: Request) -> Any:
    payload = parse_crud_payload(await request.json())
    try:
      update_crud_item_command(
        deps,
        item_id=item_id,
        name=payload['name'],
        code=payload['code'],
        remark=payload['remark'],
        status=payload['status'],
      )
    except LocalCrudServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/crud/{item_id}')
  def delete_crud_item(item_id: str) -> dict[str, Any]:
    delete_crud_item_command(deps, item_id=item_id)
    return ok_func(True, 'success')
