from __future__ import annotations

from typing import Any


def insert_work_order(
  cur: Any,
  *,
  work_order_id: str,
  work_order_no: str,
  contract_id: str,
  contract_no: str,
  customer_name: str,
  product_id: str,
  product_code: str,
  product_name: str,
  plan_quantity: float,
  status: int,
  priority: int,
  planned_start_date: str,
  planned_end_date: str,
  applicant: str,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO work_orders(
      id, work_order_no, contract_id, contract_no, customer_name, product_id, product_code, product_name,
      plan_quantity, reported_quantity, qualified_quantity, inbound_quantity, status, priority,
      planned_start_date, planned_end_date, actual_start_time, actual_end_time,
      applicant, approval_flow_id, current_node_index, remark, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?, ?, ?, '', '', ?, 0, 0, ?, ?, ?)
    ''',
    (
      work_order_id,
      work_order_no,
      contract_id,
      contract_no,
      customer_name,
      product_id,
      product_code,
      product_name,
      plan_quantity,
      status,
      priority,
      planned_start_date,
      planned_end_date,
      applicant,
      remark,
      now,
      now,
    ),
  )


def fetch_work_order_edit_guard_row(cur: Any, work_order_id: str) -> Any:
  cur.execute('SELECT status, qualified_quantity, inbound_quantity FROM work_orders WHERE id = ?', (work_order_id,))
  return cur.fetchone()


def update_work_order(
  cur: Any,
  *,
  work_order_id: str,
  work_order_no: str,
  contract_id: str,
  contract_no: str,
  customer_name: str,
  product_id: str,
  product_code: str,
  product_name: str,
  plan_quantity: float,
  priority: int,
  planned_start_date: str,
  planned_end_date: str,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE work_orders
    SET work_order_no = ?, contract_id = ?, contract_no = ?, customer_name = ?,
        product_id = ?, product_code = ?, product_name = ?, plan_quantity = ?,
        priority = ?, planned_start_date = ?, planned_end_date = ?, remark = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      work_order_no,
      contract_id,
      contract_no,
      customer_name,
      product_id,
      product_code,
      product_name,
      plan_quantity,
      priority,
      planned_start_date,
      planned_end_date,
      remark,
      now,
      work_order_id,
    ),
  )


def fetch_work_order_status_row(cur: Any, work_order_id: str) -> Any:
  cur.execute('SELECT status FROM work_orders WHERE id = ?', (work_order_id,))
  return cur.fetchone()


def fetch_work_order_submit_row(cur: Any, work_order_id: str) -> Any:
  cur.execute('SELECT id, status FROM work_orders WHERE id = ?', (work_order_id,))
  return cur.fetchone()


def update_work_order_submit_state(
  cur: Any,
  *,
  work_order_id: str,
  approval_flow_id: int,
  current_node_index: int,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE work_orders
    SET status = ?, approval_flow_id = ?, current_node_index = ?, update_time = ?
    WHERE id = ?
    ''',
    (1, approval_flow_id, current_node_index, now, work_order_id),
  )


def fetch_work_order_approval_row(cur: Any, work_order_id: str) -> Any:
  cur.execute(
    'SELECT status, approval_flow_id, current_node_index, applicant, work_order_no FROM work_orders WHERE id = ?',
    (work_order_id,),
  )
  return cur.fetchone()


def update_work_order_approved(cur: Any, *, work_order_id: str, now: str) -> None:
  cur.execute(
    'UPDATE work_orders SET status = ?, current_node_index = ?, update_time = ? WHERE id = ?',
    (2, 0, now, work_order_id),
  )


def update_work_order_current_node(cur: Any, *, work_order_id: str, current_node_index: int, now: str) -> None:
  cur.execute(
    'UPDATE work_orders SET current_node_index = ?, update_time = ? WHERE id = ?',
    (current_node_index, now, work_order_id),
  )


def update_work_order_rejected(cur: Any, *, work_order_id: str, now: str) -> None:
  cur.execute(
    'UPDATE work_orders SET status = ?, current_node_index = ?, update_time = ? WHERE id = ?',
    (6, 0, now, work_order_id),
  )


def update_work_order_cancelled(cur: Any, *, work_order_id: str, now: str) -> None:
  cur.execute(
    'UPDATE work_orders SET status = ?, current_node_index = ?, update_time = ? WHERE id = ?',
    (7, 0, now, work_order_id),
  )


def delete_work_order(cur: Any, work_order_id: str) -> None:
  cur.execute('DELETE FROM work_orders WHERE id = ?', (work_order_id,))


def fetch_work_order_for_report(cur: Any, work_order_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, work_order_no, status, plan_quantity, qualified_quantity, applicant
    FROM work_orders
    WHERE id = ?
    LIMIT 1
    ''',
    (work_order_id,),
  )
  return cur.fetchone()


def update_work_order_report_metrics(
  cur: Any,
  *,
  work_order_id: str,
  report_quantity: float,
  qualified_quantity: float,
  status: int,
  now: str,
  actual_start_time: str | None,
  actual_end_time: str | None,
) -> None:
  set_sql = '''
    UPDATE work_orders
    SET reported_quantity = reported_quantity + ?,
        qualified_quantity = qualified_quantity + ?,
        status = ?,
        update_time = ?
  '''
  set_args: list[Any] = [report_quantity, qualified_quantity, status, now]
  if actual_start_time is not None:
    set_sql += ', actual_start_time = ?'
    set_args.append(actual_start_time)
  if actual_end_time is not None:
    set_sql += ', actual_end_time = ?'
    set_args.append(actual_end_time)
  set_sql += ' WHERE id = ?'
  set_args.append(work_order_id)
  cur.execute(set_sql, tuple(set_args))


def fetch_work_order_for_inbound(cur: Any, work_order_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, work_order_no, product_code, product_name, customer_name,
           qualified_quantity, inbound_quantity, status, applicant
    FROM work_orders
    WHERE id = ?
    LIMIT 1
    ''',
    (work_order_id,),
  )
  return cur.fetchone()


def increment_work_order_inbound_quantity(cur: Any, *, work_order_id: str, quantity: float, now: str) -> None:
  cur.execute(
    'UPDATE work_orders SET inbound_quantity = inbound_quantity + ?, update_time = ? WHERE id = ?',
    (quantity, now, work_order_id),
  )


def fetch_work_order_quantity_row(cur: Any, work_order_id: str) -> Any:
  cur.execute('SELECT qualified_quantity, inbound_quantity FROM work_orders WHERE id = ?', (work_order_id,))
  return cur.fetchone()


def complete_work_order(cur: Any, *, work_order_id: str, now: str) -> None:
  cur.execute(
    'UPDATE work_orders SET status = ?, actual_end_time = ?, update_time = ? WHERE id = ?',
    (5, now, now, work_order_id),
  )


def query_work_order_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM work_orders {where_sql}', args)
  return cur.fetchone()


def query_work_order_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, work_order_no, contract_id, contract_no, customer_name, product_id, product_code, product_name,
           plan_quantity, reported_quantity, qualified_quantity, inbound_quantity, status, priority,
           planned_start_date, planned_end_date, actual_start_time, actual_end_time,
           applicant, approval_flow_id, current_node_index, remark, create_time, update_time
    FROM work_orders
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def query_work_order_export_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT work_order_no, contract_no, customer_name, product_name, plan_quantity, reported_quantity,
           qualified_quantity, inbound_quantity, status, planned_start_date, planned_end_date, update_time
    FROM work_orders
    {where_sql}
    ORDER BY update_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def query_work_order_status_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT status FROM work_orders')
  return cur.fetchall()


def query_work_order_product_plan_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT product_name, plan_quantity FROM work_orders')
  return cur.fetchall()


def query_work_order_list_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, work_order_no, contract_id, contract_no, customer_name, product_id, product_code, product_name,
           plan_quantity, reported_quantity, qualified_quantity, inbound_quantity, status, priority,
           planned_start_date, planned_end_date, actual_start_time, actual_end_time,
           applicant, approval_flow_id, current_node_index, remark, create_time, update_time
    FROM work_orders
    {where_sql}
    ORDER BY update_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def fetch_work_order_detail_row(cur: Any, work_order_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, work_order_no, contract_id, contract_no, customer_name, product_id, product_code, product_name,
           plan_quantity, reported_quantity, qualified_quantity, inbound_quantity, status, priority,
           planned_start_date, planned_end_date, actual_start_time, actual_end_time,
           applicant, approval_flow_id, current_node_index, remark, create_time, update_time
    FROM work_orders
    WHERE id = ?
    LIMIT 1
    ''',
    (work_order_id,),
  )
  return cur.fetchone()


def fetch_work_order_approval_status_row(cur: Any, work_order_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, work_order_no, status, approval_flow_id, current_node_index
    FROM work_orders
    WHERE id = ?
    LIMIT 1
    ''',
    (work_order_id,),
  )
  return cur.fetchone()
