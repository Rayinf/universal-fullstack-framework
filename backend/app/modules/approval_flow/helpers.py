from __future__ import annotations

from typing import Any, Callable


def process_library_name_map(get_process_library_records_func: Callable[[], list[dict[str, Any]]]) -> dict[str, str]:
  return {str(item['id']): item['processName'] for item in get_process_library_records_func()}


def build_flow_name_map(rows: list[Any]) -> dict[int, str]:
  return {int(row['id']): row['approval_flow_name'] or '' for row in rows}


def build_user_name_map(rows: list[Any]) -> dict[str, str]:
  return {
    str(row['user_id']): (row['real_name'] or row['username'] or str(row['user_id']))
    for row in rows
  }


def normalize_page_params(current: int, size: int) -> tuple[int, int]:
  return max(current, 1), max(size, 1)
