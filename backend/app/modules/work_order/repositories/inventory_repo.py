from __future__ import annotations

from typing import Any


def fetch_inventory_item_by_sku(cur: Any, sku: str) -> Any:
  cur.execute('SELECT id, stock_qty FROM inventory_items WHERE sku = ?', (sku,))
  return cur.fetchone()


def update_inventory_item_stock(cur: Any, *, item_id: str, stock_qty: float, now: str) -> None:
  cur.execute('UPDATE inventory_items SET stock_qty = ?, update_time = ? WHERE id = ?', (stock_qty, now, item_id))


def insert_inventory_item(
  cur: Any,
  *,
  item_id: str,
  sku: str,
  item_name: str,
  unit: str,
  stock_qty: float,
  create_time: str,
  update_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO inventory_items(id, sku, item_name, unit, stock_qty, safety_qty, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, 0, ?, ?)
    ''',
    (item_id, sku, item_name, unit, stock_qty, create_time, update_time),
  )


def insert_inventory_transaction(
  cur: Any,
  *,
  transaction_id: str,
  item_id: str,
  sku: str,
  item_name: str,
  direction: int,
  quantity: float,
  after_stock: float,
  business_no: str,
  operator_name: str,
  remark: str,
  create_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO inventory_transactions(
      id, item_id, sku, item_name, direction, quantity, after_stock, business_no, operator_name, remark, create_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      transaction_id,
      item_id,
      sku,
      item_name,
      direction,
      quantity,
      after_stock,
      business_no,
      operator_name,
      remark,
      create_time,
    ),
  )
