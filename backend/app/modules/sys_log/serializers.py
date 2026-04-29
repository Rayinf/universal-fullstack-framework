from __future__ import annotations

from typing import Any


def sys_log_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': int(row['id']),
    'type': int(row['type'] or 1),
    'content': row['content'] or '',
    'sysLogId': row['sys_log_id'] or '',
    'creator': row['creator'] or '',
    'createBy': row['create_by'] or '',
    'realName': row['real_name'] or '',
    'username': row['real_name'] or row['creator'] or '',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
    'tenantCode': row['tenant_code'] or 'LOCAL',
  }


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': (total + size - 1) // size,
  }


def build_sys_log_export_csv(rows: list[Any]) -> str:
  lines = ['id,type,content,creator,realName,createTime']
  for row in rows:
    row_content = str(row['content'] or '').replace(',', ' ')
    lines.append(
      f"{int(row['id'])},{int(row['type'] or 1)},{row_content},{row['creator'] or ''},{row['real_name'] or ''},{row['create_time'] or ''}",
    )
  return '\n'.join(lines)
