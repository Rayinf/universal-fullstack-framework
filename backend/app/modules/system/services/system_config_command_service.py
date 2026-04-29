from __future__ import annotations

from app.modules.system.deps import SystemConfigRouterDeps
from app.modules.system.helpers import resolve_system_config_column
from app.modules.system.repositories.system_config_repo import (
  update_system_config,
  update_system_config_column,
)
from app.modules.system.services.errors import SystemServiceError


def update_system_config_single(
  deps: SystemConfigRouterDeps,
  *,
  code: str,
  value: str,
) -> bool:
  if not code:
    raise SystemServiceError('code不能为空', 400)

  target_col = resolve_system_config_column(code)
  if not target_col:
    raise SystemServiceError('不支持的配置项', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_system_config_column(cur, target_col, value)
  conn.commit()
  conn.close()
  return True


def update_system_config_all(
  deps: SystemConfigRouterDeps,
  *,
  company_name: str,
  system_name: str,
  version: str,
) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_system_config(cur, company_name=company_name, system_name=system_name, version=version)
  conn.commit()
  conn.close()
  return True
