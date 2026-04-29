from __future__ import annotations

from typing import Any


def query_payment_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(
    f'''
    SELECT COUNT(1) AS cnt
    FROM payment_records p
    LEFT JOIN contracts c ON c.id = p.contract_id
    {where_sql}
    ''',
    args,
  )
  return cur.fetchone()


def query_payment_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT p.id, p.contract_id, p.payment_no, p.payment_amount, p.payment_date, p.payment_method,
           p.payer_name, p.received_by, p.remark, p.status, p.create_time,
           c.contract_no, c.customer_name
    FROM payment_records p
    LEFT JOIN contracts c ON c.id = p.contract_id
    {where_sql}
    ORDER BY p.create_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def query_payment_export_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT p.payment_no, c.contract_no, c.customer_name, p.payment_amount, p.payment_date,
           p.payment_method, p.status, p.received_by, p.create_time
    FROM payment_records p
    LEFT JOIN contracts c ON c.id = p.contract_id
    {where_sql}
    ORDER BY p.create_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def insert_payment(
  cur: Any,
  *,
  payment_id: str,
  contract_id: str,
  payment_no: str,
  payment_amount: float,
  payment_date: str,
  payment_method: int,
  payer_name: str,
  received_by: str,
  remark: str,
  create_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO payment_records(
      id, contract_id, payment_no, payment_amount, payment_date, payment_method,
      payer_name, received_by, remark, status, create_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    ''',
    (
      payment_id,
      contract_id,
      payment_no,
      payment_amount,
      payment_date,
      payment_method,
      payer_name,
      received_by,
      remark,
      create_time,
    ),
  )


def fetch_payment_status_row(cur: Any, payment_id: str) -> Any:
  cur.execute('SELECT contract_id, status FROM payment_records WHERE id = ?', (payment_id,))
  return cur.fetchone()


def mark_payment_confirmed(cur: Any, payment_id: str) -> None:
  cur.execute('UPDATE payment_records SET status = 1 WHERE id = ?', (payment_id,))


def delete_payment(cur: Any, payment_id: str) -> None:
  cur.execute('DELETE FROM payment_records WHERE id = ?', (payment_id,))


def query_confirmed_payment_sum(cur: Any, contract_id: str) -> Any:
  cur.execute(
    'SELECT COALESCE(SUM(payment_amount), 0) AS paid FROM payment_records WHERE contract_id = ? AND status = 1',
    (contract_id,),
  )
  return cur.fetchone()


def query_dashboard_payment_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT payment_amount, create_time, status FROM payment_records')
  return cur.fetchall()
