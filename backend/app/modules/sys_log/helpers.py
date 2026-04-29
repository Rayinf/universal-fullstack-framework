from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def normalize_page_params(current: int, size: int) -> tuple[int, int]:
  return max(current, 1), max(size, 1)


def build_sys_log_filters(
  *,
  log_type: int | None,
  content: str | None,
  real_name: str | None,
  username: str | None,
  start_time: str | None,
  end_time: str | None,
) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  if log_type is not None:
    where_sql += ' AND type = ?'
    values.append(int(log_type))
  if content and content.strip():
    where_sql += ' AND content LIKE ?'
    values.append(f'%{content.strip()}%')

  name_key = (real_name or username or '').strip()
  if name_key:
    where_sql += ' AND (real_name LIKE ? OR creator LIKE ?)'
    values.extend([f'%{name_key}%', f'%{name_key}%'])

  if start_time and start_time.strip():
    where_sql += ' AND create_time >= ?'
    values.append(start_time.strip())
  if end_time and end_time.strip():
    where_sql += ' AND create_time <= ?'
    values.append(end_time.strip())

  return where_sql, values


def normalize_id_list(raw_values: list[str]) -> list[str]:
  return [item.strip() for item in raw_values if item.strip()]


def build_clear_cutoff(clear_type: int) -> str:
  days_map = {1: 7, 2: 30, 3: 90, 4: 180, 5: 365, 6: 1095}
  days = days_map.get(int(clear_type), 30)
  return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
