from __future__ import annotations

from app.modules.system.serializers import build_health_payload


def get_health_payload(*, db_driver: str) -> dict[str, str]:
  return build_health_payload(db_driver)
