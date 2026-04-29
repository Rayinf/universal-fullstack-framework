from __future__ import annotations

from typing import Any

from app.modules.sys_backup.deps import SysBackupRouterDeps
from app.modules.sys_backup.helpers import build_sys_backup_filters, normalize_page_params
from app.modules.sys_backup.repositories.sys_backup_repo import (
  fetch_latest_sys_backup_config,
  fetch_sys_backup_download,
  query_sys_backup_page_rows,
  query_sys_backup_page_total,
)
from app.modules.sys_backup.serializers import (
  build_page_result,
  sys_backup_config_to_dict,
  sys_backup_record_to_dict,
)
from app.modules.sys_backup.services.errors import SysBackupServiceError


def query_sys_backup_page(
  deps: SysBackupRouterDeps,
  *,
  current: int,
  size: int,
  name: str | None,
  type_code: int | None,
) -> dict[str, Any]:
  page_current, page_size = normalize_page_params(current, size)
  where_sql, values = build_sys_backup_filters(name=name, type_code=type_code)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  total = int(query_sys_backup_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_sys_backup_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  conn.close()
  return build_page_result([sys_backup_record_to_dict(row) for row in rows], total, page_current, page_size)


def get_sys_backup_download(deps: SysBackupRouterDeps, *, backup_id: str) -> dict[str, str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_sys_backup_download(cur, backup_id)
  conn.close()
  if not row:
    raise SysBackupServiceError('备份文件不存在', 404)
  return {
    'name': row['name'],
    'file_content': row['file_content'] or '-- empty backup',
  }


def get_sys_backup_config(deps: SysBackupRouterDeps) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_latest_sys_backup_config(cur)
  conn.close()
  if not row:
    return {}
  return sys_backup_config_to_dict(row)
