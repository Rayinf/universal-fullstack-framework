from __future__ import annotations

from typing import Any


def query_purchase_order_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM purchase_orders {where_sql}', values)
  return cur.fetchone()


def query_purchase_order_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, order_no, supplier_name, item_name, quantity, unit_price, total_amount, status,
           applicant, remark, create_time, update_time
    FROM purchase_orders
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def insert_purchase_order(
  cur: Any,
  *,
  order_id: str,
  order_no: str,
  supplier_name: str,
  item_name: str,
  quantity: float,
  unit_price: float,
  total_amount: float,
  status: int,
  applicant: str,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO purchase_orders(
      id, order_no, supplier_name, item_name, quantity, unit_price, total_amount, status,
      applicant, remark, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      order_id,
      order_no,
      supplier_name,
      item_name,
      quantity,
      unit_price,
      total_amount,
      status,
      applicant,
      remark,
      now,
      now,
    ),
  )


def fetch_purchase_order_status_row(cur: Any, order_id: str) -> Any:
  cur.execute('SELECT status FROM purchase_orders WHERE id = ?', (order_id,))
  return cur.fetchone()


def update_purchase_order(
  cur: Any,
  *,
  order_id: str,
  order_no: str,
  supplier_name: str,
  item_name: str,
  quantity: float,
  unit_price: float,
  total_amount: float,
  status: int,
  applicant: str,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE purchase_orders
    SET order_no = ?, supplier_name = ?, item_name = ?, quantity = ?, unit_price = ?, total_amount = ?,
        status = ?, applicant = ?, remark = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      order_no,
      supplier_name,
      item_name,
      quantity,
      unit_price,
      total_amount,
      status,
      applicant,
      remark,
      now,
      order_id,
    ),
  )


def fetch_purchase_order_approval_row(cur: Any, order_id: str) -> Any:
  cur.execute(
    'SELECT status, approval_flow_id, current_node_index FROM purchase_orders WHERE id = ?',
    (order_id,),
  )
  return cur.fetchone()


def update_purchase_order_submit_state(
  cur: Any,
  *,
  order_id: str,
  approval_flow_id: int,
  current_node_index: int,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE purchase_orders
    SET status = ?, approval_flow_id = ?, current_node_index = ?, update_time = ?
    WHERE id = ?
    ''',
    (1, approval_flow_id, current_node_index, now, order_id),
  )


def update_purchase_order_current_node(cur: Any, *, order_id: str, current_node_index: int, now: str) -> None:
  cur.execute(
    'UPDATE purchase_orders SET current_node_index = ?, update_time = ? WHERE id = ?',
    (current_node_index, now, order_id),
  )


def update_purchase_order_approved(cur: Any, *, order_id: str, now: str) -> None:
  cur.execute(
    'UPDATE purchase_orders SET status = ?, current_node_index = 0, update_time = ? WHERE id = ?',
    (2, now, order_id),
  )


def update_purchase_order_cancelled(cur: Any, *, order_id: str, now: str) -> None:
  cur.execute(
    'UPDATE purchase_orders SET status = ?, current_node_index = 0, update_time = ? WHERE id = ?',
    (3, now, order_id),
  )


def fetch_purchase_order_approval_status_row(cur: Any, order_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, order_no, status, approval_flow_id, current_node_index
    FROM purchase_orders
    WHERE id = ?
    ''',
    (order_id,),
  )
  return cur.fetchone()


def delete_purchase_order(cur: Any, order_id: str) -> None:
  cur.execute('DELETE FROM purchase_orders WHERE id = ?', (order_id,))
