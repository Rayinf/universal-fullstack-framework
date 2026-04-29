from __future__ import annotations

from typing import Any


def query_quotation_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM quotations {where_sql}', args)
  return cur.fetchone()


def query_quotation_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, quote_no, customer_id, customer_name, contact_person, total_amount, discount_rate,
           final_amount, validity_days, validity_end_date, status, applicant, approval_flow_id,
           current_node_index, version, remark, create_time, update_time
    FROM quotations
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def fetch_quotation_detail_row(cur: Any, quotation_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, quote_no, customer_id, customer_name, contact_person, total_amount, discount_rate,
           final_amount, validity_days, validity_end_date, status, applicant, approval_flow_id,
           current_node_index, version, remark, create_time, update_time
    FROM quotations
    WHERE id = ?
    LIMIT 1
    ''',
    (quotation_id,),
  )
  return cur.fetchone()


def insert_quotation(
  cur: Any,
  *,
  quotation_id: str,
  quote_no: str,
  customer_id: str,
  customer_name: str,
  contact_person: str,
  total_amount: float,
  discount_rate: float,
  final_amount: float,
  validity_days: int,
  validity_end_date: str,
  status: int,
  applicant: str,
  version: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO quotations(
      id, quote_no, customer_id, customer_name, contact_person, total_amount,
      discount_rate, final_amount, validity_days, validity_end_date, status,
      applicant, approval_flow_id, current_node_index, version, remark, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      quotation_id,
      quote_no,
      customer_id,
      customer_name,
      contact_person,
      total_amount,
      discount_rate,
      final_amount,
      validity_days,
      validity_end_date,
      status,
      applicant,
      0,
      0,
      version,
      remark,
      now,
      now,
    ),
  )


def fetch_quotation_edit_guard_row(cur: Any, quotation_id: str) -> Any:
  cur.execute('SELECT status, version FROM quotations WHERE id = ?', (quotation_id,))
  return cur.fetchone()


def update_quotation(
  cur: Any,
  *,
  quotation_id: str,
  quote_no: str,
  customer_id: str,
  customer_name: str,
  contact_person: str,
  total_amount: float,
  discount_rate: float,
  final_amount: float,
  validity_days: int,
  validity_end_date: str,
  status: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE quotations
    SET quote_no = ?, customer_id = ?, customer_name = ?, contact_person = ?,
        total_amount = ?, discount_rate = ?, final_amount = ?, validity_days = ?, validity_end_date = ?,
        status = ?, remark = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      quote_no,
      customer_id,
      customer_name,
      contact_person,
      total_amount,
      discount_rate,
      final_amount,
      validity_days,
      validity_end_date,
      status,
      remark,
      now,
      quotation_id,
    ),
  )


def fetch_quotation_status_row(cur: Any, quotation_id: str) -> Any:
  cur.execute('SELECT status FROM quotations WHERE id = ?', (quotation_id,))
  return cur.fetchone()


def fetch_quotation_submit_row(cur: Any, quotation_id: str) -> Any:
  cur.execute('SELECT id, status FROM quotations WHERE id = ?', (quotation_id,))
  return cur.fetchone()


def update_quotation_submit_state(
  cur: Any,
  *,
  quotation_id: str,
  approval_flow_id: int,
  current_node_index: int,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE quotations
    SET status = ?, approval_flow_id = ?, current_node_index = ?, update_time = ?
    WHERE id = ?
    ''',
    (1, approval_flow_id, current_node_index, now, quotation_id),
  )


def fetch_quotation_approval_row(cur: Any, quotation_id: str) -> Any:
  cur.execute(
    'SELECT status, approval_flow_id, current_node_index FROM quotations WHERE id = ?',
    (quotation_id,),
  )
  return cur.fetchone()


def update_quotation_approved(cur: Any, *, quotation_id: str, now: str) -> None:
  cur.execute(
    'UPDATE quotations SET status = ?, current_node_index = ?, update_time = ? WHERE id = ?',
    (2, 0, now, quotation_id),
  )


def update_quotation_current_node(cur: Any, *, quotation_id: str, current_node_index: int, now: str) -> None:
  cur.execute(
    'UPDATE quotations SET current_node_index = ?, update_time = ? WHERE id = ?',
    (current_node_index, now, quotation_id),
  )


def update_quotation_rejected(cur: Any, *, quotation_id: str, now: str) -> None:
  cur.execute(
    'UPDATE quotations SET status = ?, current_node_index = ?, update_time = ? WHERE id = ?',
    (3, 0, now, quotation_id),
  )


def update_quotation_cancelled(cur: Any, *, quotation_id: str, now: str) -> None:
  cur.execute(
    'UPDATE quotations SET status = ?, current_node_index = ?, update_time = ? WHERE id = ?',
    (5, 0, now, quotation_id),
  )


def fetch_quotation_approval_status_row(cur: Any, quotation_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, quote_no, status, approval_flow_id, current_node_index
    FROM quotations
    WHERE id = ?
    LIMIT 1
    ''',
    (quotation_id,),
  )
  return cur.fetchone()


def delete_quotation(cur: Any, quotation_id: str) -> None:
  cur.execute('DELETE FROM quotations WHERE id = ?', (quotation_id,))
