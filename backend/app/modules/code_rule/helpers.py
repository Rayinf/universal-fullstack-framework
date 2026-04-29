from __future__ import annotations

from datetime import datetime
from typing import Any


def normalize_pagination(page: int | None, current: int | None, size: int) -> tuple[int, int]:
  return max(current or page or 1, 1), max(size, 1)


def build_code_rule_filters(rule_type: int | None, keyword: str | None) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if rule_type is not None:
    where_sql += ' AND type = ?'
    values.append(int(rule_type))
  if keyword and keyword.strip():
    where_sql += ' AND (rule_name LIKE ? OR prefix LIKE ?)'
    key = f'%{keyword.strip()}%'
    values.extend([key, key])
  return where_sql, values


def parse_code_rule_payload(payload: dict[str, Any], safe_int_func: Any) -> dict[str, Any]:
  return {
    'id': str(payload.get('id', '')).strip(),
    'type': safe_int_func(payload.get('type'), 0),
    'prefix': str(payload.get('prefix', '')).strip(),
    'rule_name': str(payload.get('ruleName', '')).strip(),
    'is_enable': safe_int_func(payload.get('isEnable'), 0),
    'remark': str(payload.get('remark', '')).strip(),
  }


def generate_code_value(prefix: str) -> str:
  return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
