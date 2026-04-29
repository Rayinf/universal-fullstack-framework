from __future__ import annotations

from typing import Any


def code_rule_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': row['id'],
    'type': int(row['type']),
    'prefix': row['prefix'],
    'ruleName': row['rule_name'],
    'isEnable': int(row['is_enable'] or 0),
    'remark': row['remark'] or '',
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
