from __future__ import annotations

from typing import Any

from app.modules._template.backend_module.deps import ExampleRouterDeps
from app.modules._template.backend_module.repositories.example_repo import insert_example_record
from app.modules._template.backend_module.services.errors import ExampleModuleServiceError


def create_example_record(deps: ExampleRouterDeps, *, payload: dict[str, Any]) -> bool:
  name = str(payload.get('name', '')).strip() if isinstance(payload, dict) else ''
  if not name:
    raise ExampleModuleServiceError('name不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  insert_example_record(cur, name=name)
  conn.commit()
  conn.close()
  return True
