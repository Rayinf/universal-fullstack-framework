from __future__ import annotations

from typing import Any


def customer_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': row['id'],
    'customerCode': row['customer_code'],
    'customerName': row['customer_name'],
    'accountManagerName': row['account_manager_name'] or '',
    'introducerName': row['introducer_name'] or '',
    'customerLevel': int(row['customer_level'] or 3),
    'specialNotes': row['special_notes'] or '',
    'creator': row['creator'] or '系统管理员',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
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
