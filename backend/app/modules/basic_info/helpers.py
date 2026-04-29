from __future__ import annotations

from typing import Any


def normalize_pagination(page: int | None, current: int | None, size: int) -> tuple[int, int]:
  return max(current or page or 1, 1), max(size, 1)


def build_basic_info_filters(info_type: int | None, key_word: str | None) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if info_type is not None:
    where_sql += ' AND type = ?'
    values.append(int(info_type))
  if key_word and key_word.strip():
    where_sql += ' AND name LIKE ?'
    values.append(f'%{key_word.strip()}%')
  return where_sql, values


def parse_basic_info_payload(payload: dict[str, Any], safe_int_func: Any) -> dict[str, Any]:
  return {
    'id': safe_int_func(payload.get('id'), 0),
    'name': str(payload.get('name', '')).strip(),
    'type': safe_int_func(payload.get('type'), 0),
    'parent_id': payload.get('parentId'),
  }
