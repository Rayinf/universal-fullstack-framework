from __future__ import annotations

from typing import Any, Callable


def normalize_page_params(current: int | None, page: int | None, size: int) -> tuple[int, int]:
  return max(current or page or 1, 1), max(size, 1)


def parse_workstation_payload(
  payload: dict[str, Any],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'id': str(payload.get('id', '')).strip(),
    'workstation_no': safe_int_func(payload.get('workstationNo'), 0),
    'workstation_name': str(payload.get('workstationName', '')).strip(),
    'workstation_type': safe_int_func(payload.get('workstationType'), 1),
    'status': safe_int_func(payload.get('status'), 1),
    'responsible_person': str(payload.get('responsiblePerson', '')).strip(),
    'dept_id': str(payload.get('deptId', '')).strip(),
    'process_library_id': str(payload.get('processLibraryId', '')).strip(),
    'remarks': str(payload.get('remarks', '')).strip(),
  }
