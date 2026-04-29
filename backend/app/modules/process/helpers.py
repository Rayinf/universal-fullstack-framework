from __future__ import annotations

from typing import Any


def filter_process_library_records(records: list[dict[str, Any]], keyword: str | None) -> list[dict[str, Any]]:
  if not keyword or not keyword.strip():
    return records
  needle = keyword.strip()
  return [item for item in records if needle in str(item.get('processName', ''))]


def normalize_page_args(current: int, size: int) -> tuple[int, int]:
  return max(current, 1), max(size, 1)


def slice_page_records(records: list[dict[str, Any]], current: int, size: int) -> list[dict[str, Any]]:
  offset = (current - 1) * size
  return records[offset : offset + size]
