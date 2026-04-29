from __future__ import annotations

from typing import Any


def notification_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'userId': str(row['user_id']),
    'title': row['title'],
    'content': row['content'] or '',
    'type': int(row['type']),
    'bizType': row['biz_type'] or '',
    'bizId': row['biz_id'] or '',
    'isRead': int(row['is_read']),
    'createTime': row['create_time'] or '',
  }


def build_notification_page_result(
  records: list[dict[str, Any]],
  total: int,
  current: int,
  size: int,
) -> dict[str, Any]:
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': (total + size - 1) // size if size else 0,
  }
