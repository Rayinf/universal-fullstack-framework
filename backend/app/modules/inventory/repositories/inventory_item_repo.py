from __future__ import annotations

from typing import Any


def query_inventory_item_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM inventory_items {where_sql}', values)
  return cur.fetchone()


def query_inventory_item_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, sku, item_name, unit, stock_qty, safety_qty, create_time, update_time
    FROM inventory_items
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_inventory_summary_rows(cur: Any, where_sql: str, values: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, sku, item_name, unit, stock_qty, safety_qty, create_time, update_time
    FROM inventory_items
    {where_sql}
    ORDER BY update_time DESC
    ''',
    values,
  )
  return cur.fetchall()


def insert_inventory_item(
  cur: Any,
  *,
  item_id: str,
  sku: str,
  item_name: str,
  unit: str,
  stock_qty: float,
  safety_qty: float,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO inventory_items(id, sku, item_name, unit, stock_qty, safety_qty, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (item_id, sku, item_name, unit, stock_qty, safety_qty, now, now),
  )


def fetch_inventory_item_id(cur: Any, item_id: str) -> Any:
  cur.execute('SELECT id FROM inventory_items WHERE id = ?', (item_id,))
  return cur.fetchone()


def update_inventory_item(
  cur: Any,
  *,
  item_id: str,
  sku: str,
  item_name: str,
  unit: str,
  stock_qty: float,
  safety_qty: float,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE inventory_items
    SET sku = ?, item_name = ?, unit = ?, stock_qty = ?, safety_qty = ?, update_time = ?
    WHERE id = ?
    ''',
    (sku, item_name, unit, stock_qty, safety_qty, now, item_id),
  )


def fetch_inventory_item_for_transaction_by_id(cur: Any, item_id: str) -> Any:
  cur.execute('SELECT id, sku, item_name, stock_qty FROM inventory_items WHERE id = ?', (item_id,))
  return cur.fetchone()


def fetch_inventory_item_for_transaction_by_sku(cur: Any, sku: str) -> Any:
  cur.execute('SELECT id, sku, item_name, stock_qty FROM inventory_items WHERE sku = ?', (sku,))
  return cur.fetchone()


def update_inventory_item_stock(cur: Any, *, item_id: str, stock_qty: float, now: str) -> None:
  cur.execute(
    'UPDATE inventory_items SET stock_qty = ?, update_time = ? WHERE id = ?',
    (stock_qty, now, item_id),
  )


def delete_inventory_item(cur: Any, item_id: str) -> None:
  cur.execute('DELETE FROM inventory_items WHERE id = ?', (item_id,))
