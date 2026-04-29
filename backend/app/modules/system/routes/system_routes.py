from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.modules.system.deps import SystemRouterDeps
from app.modules.system.serializers import HealthDocResponse
from app.modules.system.services.system_query_service import get_health_payload


def register_system_routes(router: APIRouter, deps: SystemRouterDeps) -> None:
  @router.get('/health', response_model=HealthDocResponse)
  def health() -> dict[str, Any]:
    return deps.ok_func(get_health_payload(db_driver=deps.db_driver), 'success')
