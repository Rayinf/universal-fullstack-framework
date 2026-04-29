from __future__ import annotations

from typing import Any, Callable


def build_customer_page_filters(
  customer_code: str | None,
  search_key: str | None,
  customer_level: int | None,
  start_date: str | None,
  end_date: str | None,
) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  if customer_code and customer_code.strip():
    where_sql += ' AND customer_code LIKE ?'
    values.append(f'%{customer_code.strip()}%')
  if search_key and search_key.strip():
    where_sql += ' AND (customer_name LIKE ? OR account_manager_name LIKE ? OR introducer_name LIKE ?)'
    keyword = f'%{search_key.strip()}%'
    values.extend([keyword, keyword, keyword])
  if customer_level is not None:
    where_sql += ' AND customer_level = ?'
    values.append(int(customer_level))
  if start_date and start_date.strip():
    where_sql += ' AND substr(create_time, 1, 10) >= ?'
    values.append(start_date.strip())
  if end_date and end_date.strip():
    where_sql += ' AND substr(create_time, 1, 10) <= ?'
    values.append(end_date.strip())

  return where_sql, values


def parse_customer_payload(
  payload: dict[str, Any],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'customer_id': str(payload.get('id', '')).strip(),
    'customer_code': str(payload.get('customerCode', '')).strip(),
    'customer_name': str(payload.get('customerName', '')).strip(),
    'account_manager_name': str(payload.get('accountManagerName', '')).strip(),
    'introducer_name': str(payload.get('introducerName', '')).strip(),
    'customer_level': safe_int_func(payload.get('customerLevel'), 3),
    'special_notes': str(payload.get('specialNotes', '')).strip(),
  }
