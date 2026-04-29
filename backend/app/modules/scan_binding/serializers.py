from __future__ import annotations

from typing import Any


def scan_binding_to_dict(row: Any, process_map: dict[int, str]) -> dict[str, Any]:
  return {
    'id': int(row['id']),
    'scanAssetNumber': row['scan_asset_number'],
    'identifier': row['identifier'],
    'processId': int(row['process_id']),
    'processName': process_map.get(int(row['process_id']), ''),
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def build_scan_binding_page_result(
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
    'pages': (total + size - 1) // size,
  }
