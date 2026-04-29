from __future__ import annotations

from fastapi import APIRouter, Request

from app.modules._template.backend_module.deps import ExampleRouterDeps
from app.modules._template.backend_module.services.errors import ExampleModuleServiceError
from app.modules._template.backend_module.services.example_command_service import create_example_record
from app.modules._template.backend_module.services.example_query_service import query_example_page


def register_example_routes(router: APIRouter, deps: ExampleRouterDeps) -> None:
  @router.get('/example/page')
  def page_example(current: int = 1, size: int = 10) -> dict[str, object]:
    return deps.ok_func(query_example_page(deps, current=current, size=size), 'success')

  @router.post('/example')
  async def create_example(request: Request) -> object:
    try:
      payload = await request.json()
      return deps.ok_func(create_example_record(deps, payload=payload), 'success')
    except ExampleModuleServiceError as error:
      return deps.fail_func(error.message, error.code)
