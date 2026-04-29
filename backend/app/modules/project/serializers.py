from __future__ import annotations

from typing import Any


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  pages = (total + size - 1) // size if size > 0 else 0
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': pages,
  }


def project_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': row['id'],
    'projectCode': row['project_code'],
    'projectName': row['project_name'],
    'ownerName': row['owner_name'] or '',
    'priority': int(row['priority'] or 2),
    'status': int(row['status'] or 0),
    'progress': int(row['progress'] or 0),
    'startDate': row['start_date'] or '',
    'endDate': row['end_date'] or '',
    'remark': row['remark'] or '',
    'createTime': row['create_time'],
    'updateTime': row['update_time'],
  }
