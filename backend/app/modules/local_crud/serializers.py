from __future__ import annotations

from typing import Any


def crud_item_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': row['id'],
    'name': row['name'],
    'code': row['code'],
    'remark': row['remark'] or '',
    'status': int(row['status'] or 0),
    'createTime': row['create_time'],
    'updateTime': row['update_time'],
  }


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  pages = (total + size - 1) // size if size > 0 else 0
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': pages,
  }
