from __future__ import annotations

from typing import Any, Callable


def build_page_filters(
  keyword: str | None,
  device_category_id: str | None,
  status: int | None,
  workstation_id: str | None,
) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  if keyword and keyword.strip():
    where_sql += ' AND (device_name LIKE ? OR device_number LIKE ?)'
    key = f'%{keyword.strip()}%'
    values.extend([key, key])
  if device_category_id and str(device_category_id).strip():
    where_sql += ' AND device_category_id = ?'
    values.append(str(device_category_id).strip())
  if status is not None:
    where_sql += ' AND status = ?'
    values.append(int(status))
  if workstation_id and str(workstation_id).strip():
    where_sql += ' AND workstation_id = ?'
    values.append(str(workstation_id).strip())

  return where_sql, values


def parse_device_payload(
  payload: dict[str, Any],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'device_id': str(payload.get('id', '')).strip(),
    'device_name': str(payload.get('deviceName', '')).strip(),
    'device_number': str(payload.get('deviceNumber', '')).strip(),
    'model': str(payload.get('model', '')).strip(),
    'device_category_id': str(payload.get('deviceCategoryId', '')).strip(),
    'workstation_id': str(payload.get('workstationId', '')).strip(),
    'responsible_person': str(payload.get('responsiblePerson', '')).strip(),
    'status': safe_int_func(payload.get('status'), 1),
    'remarks': str(payload.get('remarks', '')).strip(),
    'scrap_reason': str(payload.get('scrapReason', '')).strip(),
  }
