from __future__ import annotations

from typing import Any


def build_process_library_page(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': (total + size - 1) // size if size > 0 else 0,
  }
