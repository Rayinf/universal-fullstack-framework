from __future__ import annotations

from typing import Any


def query_commission_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM commission_records {where_sql}', args)
  return cur.fetchone()


def query_commission_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, contract_id, contract_no, customer_name, salesperson_id, salesperson_name,
           contract_amount, payment_amount, commission_rate, commission_amount,
           status, pay_date, remark, create_time
    FROM commission_records
    {where_sql}
    ORDER BY create_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def query_commission_export_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT contract_no, customer_name, salesperson_name, contract_amount, payment_amount,
           commission_rate, commission_amount, status, pay_date, create_time
    FROM commission_records
    {where_sql}
    ORDER BY create_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def insert_commission(
  cur: Any,
  *,
  commission_id: str,
  contract_id: str,
  contract_no: str,
  customer_name: str,
  salesperson_id: str,
  salesperson_name: str,
  contract_amount: float,
  payment_amount: float,
  commission_rate: float,
  commission_amount: float,
  remark: str,
  create_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO commission_records(
      id, contract_id, contract_no, customer_name, salesperson_id, salesperson_name,
      contract_amount, payment_amount, commission_rate, commission_amount,
      status, pay_date, remark, create_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '', ?, ?)
    ''',
    (
      commission_id,
      contract_id,
      contract_no,
      customer_name,
      salesperson_id,
      salesperson_name,
      contract_amount,
      payment_amount,
      commission_rate,
      commission_amount,
      remark,
      create_time,
    ),
  )


def fetch_commission_status_row(cur: Any, commission_id: str) -> Any:
  cur.execute('SELECT status FROM commission_records WHERE id = ?', (commission_id,))
  return cur.fetchone()


def update_commission_paid(cur: Any, *, commission_id: str, pay_date: str) -> None:
  cur.execute('UPDATE commission_records SET status = 1, pay_date = ? WHERE id = ?', (pay_date, commission_id))


def delete_commission(cur: Any, commission_id: str) -> None:
  cur.execute('DELETE FROM commission_records WHERE id = ?', (commission_id,))


def query_commission_summary_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT salesperson_name,
           COUNT(1) AS record_count,
           COALESCE(SUM(commission_amount), 0) AS total_commission,
           COALESCE(SUM(CASE WHEN status = 1 THEN commission_amount ELSE 0 END), 0) AS paid_commission,
           COALESCE(SUM(CASE WHEN status = 0 THEN commission_amount ELSE 0 END), 0) AS pending_commission
    FROM commission_records
    GROUP BY salesperson_name
    ORDER BY total_commission DESC
    ''',
  )
  return cur.fetchall()


def query_dashboard_commission_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT salesperson_name, commission_amount FROM commission_records')
  return cur.fetchall()
