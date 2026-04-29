from __future__ import annotations

from typing import Any


def table_columns(cur: Any, table_name: str) -> set[str]:
  cur.execute(f'PRAGMA table_info({table_name})')
  return {str(row['name']) for row in cur.fetchall()}
