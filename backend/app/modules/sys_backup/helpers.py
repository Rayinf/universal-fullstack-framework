from __future__ import annotations

from typing import Any

from app.modules.sys_backup.deps import SysBackupRouterDeps


def normalize_page_params(current: int, size: int) -> tuple[int, int]:
  return max(current, 1), max(size, 1)


def build_sys_backup_filters(*, name: str | None, type_code: int | None) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if name and name.strip():
    where_sql += ' AND name LIKE ?'
    values.append(f'%{name.strip()}%')
  if type_code is not None:
    where_sql += ' AND type = ?'
    values.append(int(type_code))
  return where_sql, values


def parse_sys_backup_config_payload(deps: SysBackupRouterDeps, payload: dict[str, Any]) -> dict[str, Any]:
  return {
    'plan_id': str(payload.get('id') or 'plan-1'),
    'name': str(payload.get('name') or '默认备份计划'),
    'enabled': 1 if payload.get('enabled', True) else 0,
    'cron_expression': str(payload.get('cronExpression') or '0 0 2 * * ?'),
    'retention_days': deps.safe_int_func(payload.get('retentionDays'), 30),
  }
