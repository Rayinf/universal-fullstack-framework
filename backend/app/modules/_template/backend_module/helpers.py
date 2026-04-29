from __future__ import annotations


def normalize_page_args(current: int, size: int) -> tuple[int, int]:
  return max(current, 1), max(size, 1)
