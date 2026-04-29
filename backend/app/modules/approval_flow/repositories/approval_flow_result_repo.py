from __future__ import annotations

from typing import Any


def query_approval_flow_result_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM approval_flow_results {where_sql}', values)
  return cur.fetchone()


def query_approval_flow_result_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, order_id, result_type, order_scheduling_id, order_name, product_name, process_library_id,
           approval_flow_id, process_people, approval_status, approval_remarks, creator, create_time
    FROM approval_flow_results
    {where_sql}
    ORDER BY create_time DESC, id DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_recent_approval_result_rows(cur: Any, where_sql: str, values: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, order_id, order_name, product_name, create_time
    FROM approval_flow_results
    {where_sql}
    ORDER BY create_time DESC, id DESC
    LIMIT 20
    ''',
    values,
  )
  return cur.fetchall()


def fetch_approval_result_by_id(cur: Any, record_id: int) -> Any:
  cur.execute('SELECT id FROM approval_flow_results WHERE id = ?', (record_id,))
  return cur.fetchone()


def update_approval_result(
  cur: Any,
  *,
  record_id: int,
  order_id: str,
  order_scheduling_id: str,
  order_name: str,
  product_name: str,
  process_library_id: str,
  approval_flow_id: int | None,
  process_people: str,
  approval_status: int,
  approval_remarks: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE approval_flow_results
    SET order_id = ?, result_type = ?, order_scheduling_id = ?, order_name = ?, product_name = ?,
        process_library_id = ?, approval_flow_id = ?, process_people = ?, approval_status = ?,
        approval_remarks = ?, creator = ?, create_time = ?
    WHERE id = ?
    ''',
    (
      order_id,
      2,
      order_scheduling_id,
      order_name,
      product_name,
      process_library_id,
      approval_flow_id,
      process_people,
      approval_status,
      approval_remarks,
      '系统管理员',
      now,
      record_id,
    ),
  )


def insert_approval_result(
  cur: Any,
  *,
  order_id: str,
  order_scheduling_id: str,
  order_name: str,
  product_name: str,
  process_library_id: str,
  approval_flow_id: int | None,
  process_people: str,
  approval_status: int,
  approval_remarks: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO approval_flow_results(
      order_id, result_type, order_scheduling_id, order_name, product_name, process_library_id,
      approval_flow_id, process_people, approval_status, approval_remarks, creator, create_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      order_id,
      2,
      order_scheduling_id,
      order_name,
      product_name,
      process_library_id,
      approval_flow_id,
      process_people,
      approval_status,
      approval_remarks,
      '系统管理员',
      now,
    ),
  )


def fetch_latest_order_scheduling_result(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(
    f'''
    SELECT id, order_id, result_type, order_scheduling_id, order_name, product_name, process_library_id,
           approval_flow_id, process_people, approval_status, approval_remarks, creator, create_time
    FROM approval_flow_results
    {where_sql}
    ORDER BY create_time DESC, id DESC
    LIMIT 1
    ''',
    values,
  )
  return cur.fetchone()


def fetch_order_scheduling_result_rows(cur: Any, order_scheduling_id: str) -> list[Any]:
  cur.execute(
    '''
    SELECT id, order_id, result_type, order_scheduling_id, order_name, product_name, process_library_id,
           approval_flow_id, process_people, approval_status, approval_remarks, creator, create_time
    FROM approval_flow_results
    WHERE order_scheduling_id = ?
    ORDER BY create_time DESC, id DESC
    ''',
    (order_scheduling_id,),
  )
  return cur.fetchall()
