from __future__ import annotations

from typing import Any

from app.modules.inventory.deps import InventoryRouterDeps
from app.modules.inventory.helpers import build_keyword_filter
from app.modules.inventory.repositories.inventory_item_repo import (
  query_inventory_item_page_rows,
  query_inventory_item_page_total,
  query_inventory_summary_rows,
)
from app.modules.inventory.repositories.inventory_transaction_repo import (
  query_inventory_transaction_page_rows,
  query_inventory_transaction_page_total,
)
from app.modules.inventory.serializers import build_page_result, inventory_item_to_dict, inventory_tx_to_dict


def query_inventory_item_page(
  deps: InventoryRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  keyword_sql, keyword_values = build_keyword_filter(keyword, ('sku', 'item_name'))
  where_sql += keyword_sql
  values.extend(keyword_values)

  total = deps.safe_int_func(query_inventory_item_page_total(cur, where_sql, tuple(values))['cnt'], 0)
  rows = query_inventory_item_page_rows(cur, where_sql, tuple(values), size, (current - 1) * size)
  conn.close()
  return build_page_result(
    [inventory_item_to_dict(row, deps.safe_float_func) for row in rows],
    total,
    current,
    size,
  )


def query_inventory_summary(
  deps: InventoryRouterDeps,
  *,
  keyword: str | None,
  low_stock_only: int | None,
) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  keyword_sql, keyword_values = build_keyword_filter(keyword, ('sku', 'item_name'))
  where_sql += keyword_sql
  values.extend(keyword_values)

  if low_stock_only and int(low_stock_only) == 1:
    where_sql += ' AND stock_qty <= safety_qty'

  rows = query_inventory_summary_rows(cur, where_sql, tuple(values))
  conn.close()
  return [inventory_item_to_dict(row, deps.safe_float_func) for row in rows]


def query_inventory_transaction_page(
  deps: InventoryRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
  direction: int | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  keyword_sql, keyword_values = build_keyword_filter(keyword, ('sku', 'item_name', 'business_no'))
  where_sql += keyword_sql
  values.extend(keyword_values)

  if direction is not None and direction in (1, 2):
    where_sql += ' AND direction = ?'
    values.append(direction)

  total = deps.safe_int_func(query_inventory_transaction_page_total(cur, where_sql, tuple(values))['cnt'], 0)
  rows = query_inventory_transaction_page_rows(cur, where_sql, tuple(values), size, (current - 1) * size)
  conn.close()
  return build_page_result(
    [inventory_tx_to_dict(row, deps.safe_float_func) for row in rows],
    total,
    current,
    size,
  )
