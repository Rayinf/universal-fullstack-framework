from __future__ import annotations

from typing import Any


def workstation_to_dict(
  row: Any,
  user_map: dict[str, str],
  dept_map: dict[str, str],
) -> dict[str, Any]:
  return {
    'id': row['id'],
    'workstationNo': int(row['workstation_no'] or 0),
    'workstationName': row['workstation_name'],
    'workstationType': int(row['workstation_type'] or 1),
    'status': int(row['status'] or 0),
    'responsiblePerson': str(row['responsible_person'] or ''),
    'responsiblePersonName': user_map.get(str(row['responsible_person'] or ''), ''),
    'deptId': str(row['dept_id'] or ''),
    'deptName': dept_map.get(str(row['dept_id'] or ''), ''),
    'processLibraryId': str(row['process_library_id'] or ''),
    'remarks': row['remarks'] or '',
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
