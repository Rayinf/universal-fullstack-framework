from __future__ import annotations

from typing import Any


def basic_info_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': int(row['id']),
    'name': row['name'],
    'type': int(row['type']),
    'parentId': int(row['parent_id']) if row['parent_id'] is not None else None,
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': (total + size - 1) // size,
  }
