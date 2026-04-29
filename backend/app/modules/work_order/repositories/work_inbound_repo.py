from __future__ import annotations

from typing import Any


def count_work_inbounds_by_work_order(cur: Any, work_order_id: str) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM work_inbounds WHERE work_order_id = ?', (work_order_id,))
  return cur.fetchone()


def insert_work_inbound(
  cur: Any,
  *,
  inbound_id: str,
  inbound_no: str,
  work_order_id: str,
  work_order_no: str,
  quantity: float,
  warehouse_name: str,
  operator_name: str,
  inbound_time: str,
  remark: str,
  create_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO work_inbounds(
      id, inbound_no, work_order_id, work_order_no, quantity,
      warehouse_name, operator_name, inbound_time, remark, create_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      inbound_id,
      inbound_no,
      work_order_id,
      work_order_no,
      quantity,
      warehouse_name,
      operator_name,
      inbound_time,
      remark,
      create_time,
    ),
  )


def query_work_inbound_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(
    f'''
    SELECT COUNT(1) AS cnt
    FROM work_inbounds wi
    LEFT JOIN work_orders wo ON wo.id = wi.work_order_id
    {where_sql}
    ''',
    args,
  )
  return cur.fetchone()


def query_work_inbound_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT wi.id, wi.inbound_no, wi.work_order_id, wi.work_order_no, wi.quantity,
           wi.warehouse_name, wi.operator_name, wi.inbound_time, wi.remark, wi.create_time,
           wo.product_name, wo.customer_name
    FROM work_inbounds wi
    LEFT JOIN work_orders wo ON wo.id = wi.work_order_id
    {where_sql}
    ORDER BY wi.create_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def query_work_inbound_export_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT wi.inbound_no, wi.work_order_no, wo.product_name, wo.customer_name,
           wi.quantity, wi.warehouse_name, wi.operator_name, wi.inbound_time, wi.remark
    FROM work_inbounds wi
    LEFT JOIN work_orders wo ON wo.id = wi.work_order_id
    {where_sql}
    ORDER BY wi.create_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def query_inbound_trend_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT inbound_time, quantity FROM work_inbounds')
  return cur.fetchall()
