from __future__ import annotations

from typing import Any


def fetch_system_config(cur: Any) -> Any:
  cur.execute('SELECT company_name, system_name, version FROM system_config WHERE id = 1')
  return cur.fetchone()


def update_system_config_column(cur: Any, column_name: str, value: str) -> None:
  cur.execute(f'UPDATE system_config SET {column_name} = ? WHERE id = 1', (value,))


def update_system_config(
  cur: Any,
  *,
  company_name: str,
  system_name: str,
  version: str,
) -> None:
  cur.execute(
    'UPDATE system_config SET company_name = ?, system_name = ?, version = ? WHERE id = 1',
    (company_name, system_name, version),
  )
