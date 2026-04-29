from __future__ import annotations

from typing import Any


def query_inventory_transaction_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM inventory_transactions {where_sql}', values)
  return cur.fetchone()


def query_inventory_transaction_page_rows(
  cur: Any,
  where_sql: str,
  values: tuple[Any, ...],
  size: int,
  offset: int,
) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, item_id, sku, item_name, direction, quantity, after_stock, business_no, operator_name, remark, create_time
    FROM inventory_transactions
    {where_sql}
    ORDER BY create_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def count_inventory_transactions_by_item(cur: Any, item_id: str) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM inventory_transactions WHERE item_id = ?', (item_id,))
  return cur.fetchone()


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
  now: str,
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
      now,
    ),
  )
