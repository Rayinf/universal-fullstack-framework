from __future__ import annotations

from typing import Any


def count_work_reports_by_work_order(cur: Any, work_order_id: str) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM work_reports WHERE work_order_id = ?', (work_order_id,))
  return cur.fetchone()


def insert_work_report(
  cur: Any,
  *,
  report_id: str,
  work_order_id: str,
  work_order_no: str,
  process_name: str,
  report_quantity: float,
  qualified_quantity: float,
  defect_quantity: float,
  report_user_id: str,
  report_user_name: str,
  report_time: str,
  remark: str,
  create_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO work_reports(
      id, work_order_id, work_order_no, process_name, report_quantity, qualified_quantity,
      defect_quantity, report_user_id, report_user_name, report_time, remark, create_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      report_id,
      work_order_id,
      work_order_no,
      process_name,
      report_quantity,
      qualified_quantity,
      defect_quantity,
      report_user_id,
      report_user_name,
      report_time,
      remark,
      create_time,
    ),
  )


def query_work_report_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(
    f'''
    SELECT COUNT(1) AS cnt
    FROM work_reports wr
    LEFT JOIN work_orders wo ON wo.id = wr.work_order_id
    {where_sql}
    ''',
    args,
  )
  return cur.fetchone()


def query_work_report_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT wr.id, wr.work_order_id, wr.work_order_no, wr.process_name,
           wr.report_quantity, wr.qualified_quantity, wr.defect_quantity, wr.report_user_id, wr.report_user_name,
           wr.report_time, wr.remark, wr.create_time,
           wo.product_name, wo.customer_name
    FROM work_reports wr
    LEFT JOIN work_orders wo ON wo.id = wr.work_order_id
    {where_sql}
    ORDER BY wr.create_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def query_work_report_export_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT wr.work_order_no, wo.product_name, wo.customer_name, wr.process_name,
           wr.report_quantity, wr.qualified_quantity, wr.defect_quantity,
           wr.report_user_name, wr.report_time, wr.remark
    FROM work_reports wr
    LEFT JOIN work_orders wo ON wo.id = wr.work_order_id
    {where_sql}
    ORDER BY wr.create_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def query_report_trend_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT report_time, qualified_quantity FROM work_reports')
  return cur.fetchall()
