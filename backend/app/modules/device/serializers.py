from __future__ import annotations

from typing import Any


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': (total + size - 1) // size,
  }


def device_to_dict(
  row: Any,
  user_map: dict[str, str],
  workstation_map: dict[str, str],
  asset_type_map: dict[str, str],
) -> dict[str, Any]:
  return {
    'id': row['id'],
    'deviceName': row['device_name'],
    'deviceNumber': row['device_number'],
    'model': row['model'],
    'deviceCategoryId': str(row['device_category_id'] or ''),
    'deviceCategoryName': asset_type_map.get(str(row['device_category_id'] or ''), ''),
    'workstationId': str(row['workstation_id'] or ''),
    'workstationName': workstation_map.get(str(row['workstation_id'] or ''), ''),
    'responsiblePerson': str(row['responsible_person'] or ''),
    'responsiblePersonName': user_map.get(str(row['responsible_person'] or ''), ''),
    'status': int(row['status'] or 1),
    'remarks': row['remarks'] or '',
    'scrapReason': row['scrap_reason'] or '',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }
