from __future__ import annotations

from typing import Any


def backup_type_text(type_code: int) -> str:
  return '自动备份' if int(type_code) == 2 else '手动备份'


def sys_backup_record_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': row['id'],
    'name': row['name'],
    'type': backup_type_text(int(row['type'] or 1)),
    'typeCode': int(row['type'] or 1),
    'status': int(row['status'] or 1),
    'createName': row['create_name'] or '系统管理员',
    'createTime': row['create_time'] or '',
    'fileName': row['name'],
    'totalSizeFormat': '32KB',
  }


def sys_backup_config_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': row['id'],
    'name': row['name'],
    'enabled': bool(int(row['enabled'] or 0)),
    'cronExpression': row['cron_expression'] or '',
    'retentionDays': int(row['retention_days'] or 30),
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
