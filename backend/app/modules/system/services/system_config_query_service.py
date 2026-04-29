from __future__ import annotations

from app.modules.system.deps import SystemConfigRouterDeps
from app.modules.system.repositories.system_config_repo import fetch_system_config
from app.modules.system.serializers import serialize_system_config


def get_tenant_name() -> str:
  return '本地MES租户'


def get_system_default_data(deps: SystemConfigRouterDeps) -> dict[str, str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_system_config(cur)
  conn.close()
  return serialize_system_config(row)
