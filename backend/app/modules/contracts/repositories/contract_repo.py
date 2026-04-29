from __future__ import annotations

from typing import Any


def query_contract_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM contracts {where_sql}', args)
  return cur.fetchone()


def query_contract_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, contract_no, quotation_id, customer_id, customer_name, contract_name,
           total_amount, paid_amount, signed_date, start_date, end_date, payment_terms,
           status, expire_warning_sent, remark, create_time, update_time
    FROM contracts
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def query_contract_export_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT contract_no, customer_name, contract_name, total_amount, paid_amount, signed_date, start_date,
           end_date, status, update_time
    FROM contracts
    {where_sql}
    ORDER BY update_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def fetch_contract_detail_row(cur: Any, contract_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, contract_no, quotation_id, customer_id, customer_name, contract_name,
           total_amount, paid_amount, signed_date, start_date, end_date, payment_terms,
           status, expire_warning_sent, remark, create_time, update_time
    FROM contracts
    WHERE id = ?
    LIMIT 1
    ''',
    (contract_id,),
  )
  return cur.fetchone()


def insert_contract(
  cur: Any,
  *,
  contract_id: str,
  contract_no: str,
  quotation_id: str,
  customer_id: str,
  customer_name: str,
  contract_name: str,
  total_amount: float,
  signed_date: str,
  start_date: str,
  end_date: str,
  payment_terms: str,
  status: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO contracts(
      id, contract_no, quotation_id, customer_id, customer_name, contract_name,
      total_amount, paid_amount, signed_date, start_date, end_date, payment_terms,
      status, expire_warning_sent, remark, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, 0, ?, ?, ?)
    ''',
    (
      contract_id,
      contract_no,
      quotation_id,
      customer_id,
      customer_name,
      contract_name,
      total_amount,
      signed_date,
      start_date,
      end_date,
      payment_terms,
      status,
      remark,
      now,
      now,
    ),
  )


def fetch_quote_for_contract_conversion(cur: Any, quotation_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, quote_no, customer_id, customer_name, final_amount, status
    FROM quotations
    WHERE id = ?
    LIMIT 1
    ''',
    (quotation_id,),
  )
  return cur.fetchone()


def insert_contract_from_quotation(
  cur: Any,
  *,
  contract_id: str,
  contract_no: str,
  quotation_id: str,
  customer_id: str,
  customer_name: str,
  contract_name: str,
  total_amount: float,
  signed_date: str,
  start_date: str,
  end_date: str,
  payment_terms: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO contracts(
      id, contract_no, quotation_id, customer_id, customer_name, contract_name,
      total_amount, paid_amount, signed_date, start_date, end_date, payment_terms,
      status, expire_warning_sent, remark, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, 1, 0, '', ?, ?)
    ''',
    (
      contract_id,
      contract_no,
      quotation_id,
      customer_id,
      customer_name,
      contract_name,
      total_amount,
      signed_date,
      start_date,
      end_date,
      payment_terms,
      now,
      now,
    ),
  )


def update_quotation_status_for_contract(cur: Any, quotation_id: str, *, status: int, now: str) -> None:
  cur.execute('UPDATE quotations SET status = ?, update_time = ? WHERE id = ?', (status, now, quotation_id))


def update_contract(
  cur: Any,
  *,
  contract_id: str,
  contract_no: str,
  customer_id: str,
  customer_name: str,
  contract_name: str,
  total_amount: float,
  signed_date: str,
  start_date: str,
  end_date: str,
  payment_terms: str,
  status: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE contracts
    SET contract_no = ?, customer_id = ?, customer_name = ?, contract_name = ?, total_amount = ?,
        signed_date = ?, start_date = ?, end_date = ?, payment_terms = ?, status = ?, remark = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      contract_no,
      customer_id,
      customer_name,
      contract_name,
      total_amount,
      signed_date,
      start_date,
      end_date,
      payment_terms,
      status,
      remark,
      now,
      contract_id,
    ),
  )


def count_payment_records_by_contract(cur: Any, contract_id: str) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM payment_records WHERE contract_id = ?', (contract_id,))
  return cur.fetchone()


def delete_contract(cur: Any, contract_id: str) -> None:
  cur.execute('DELETE FROM contracts WHERE id = ?', (contract_id,))


def delete_commissions_by_contract(cur: Any, contract_id: str) -> None:
  cur.execute('DELETE FROM commission_records WHERE contract_id = ?', (contract_id,))


def fetch_contract_exists_row(cur: Any, contract_id: str) -> Any:
  cur.execute('SELECT id FROM contracts WHERE id = ?', (contract_id,))
  return cur.fetchone()


def update_contract_terminated(cur: Any, *, contract_id: str, remark: str, now: str) -> None:
  cur.execute(
    'UPDATE contracts SET status = 4, remark = ?, update_time = ? WHERE id = ?',
    (remark, now, contract_id),
  )


def query_contract_payment_summary_rows(cur: Any, where_sql: str, args: tuple[Any, ...]) -> list[Any]:
  cur.execute(
    f'''
    SELECT c.id AS contract_id, c.contract_no, c.customer_name, c.total_amount, c.paid_amount,
           CASE WHEN c.total_amount > 0 THEN ROUND((c.paid_amount * 100.0 / c.total_amount), 2) ELSE 0 END AS paid_rate
    FROM contracts c
    {where_sql}
    ORDER BY c.update_time DESC
    ''',
    args,
  )
  return cur.fetchall()


def query_expiring_contract_rows(cur: Any, today: str, deadline: str) -> list[Any]:
  cur.execute(
    '''
    SELECT id, contract_no, customer_name, end_date, status, expire_warning_sent
    FROM contracts
    WHERE status IN (1, 2) AND end_date IS NOT NULL AND end_date != ''
      AND end_date >= ? AND end_date <= ?
    ORDER BY end_date ASC
    ''',
    (today, deadline),
  )
  return cur.fetchall()


def mark_contract_expire_warning_sent(cur: Any, *, contract_id: str, now: str) -> None:
  cur.execute('UPDATE contracts SET expire_warning_sent = 1, update_time = ? WHERE id = ?', (now, contract_id))


def query_dashboard_quotation_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT status, total_amount, create_time FROM quotations')
  return cur.fetchall()


def query_dashboard_contract_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT total_amount, paid_amount, status, end_date FROM contracts')
  return cur.fetchall()


def query_dashboard_customer_amount_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT customer_name, total_amount FROM contracts')
  return cur.fetchall()


def fetch_contract_id_row(cur: Any, contract_id: str) -> Any:
  cur.execute('SELECT id FROM contracts WHERE id = ?', (contract_id,))
  return cur.fetchone()


def fetch_contract_total_amount_row(cur: Any, contract_id: str) -> Any:
  cur.execute('SELECT total_amount FROM contracts WHERE id = ?', (contract_id,))
  return cur.fetchone()


def update_contract_paid_amount(cur: Any, *, contract_id: str, paid_amount: float, now: str) -> None:
  cur.execute(
    'UPDATE contracts SET paid_amount = ?, update_time = ? WHERE id = ?',
    (paid_amount, now, contract_id),
  )


def update_contract_status(cur: Any, *, contract_id: str, status: int, now: str) -> None:
  cur.execute(f'UPDATE contracts SET status = {int(status)}, update_time = ? WHERE id = ?', (now, contract_id))


def fetch_contract_commission_source(cur: Any, contract_id: str) -> Any:
  cur.execute(
    'SELECT contract_no, customer_name, total_amount, paid_amount FROM contracts WHERE id = ?',
    (contract_id,),
  )
  return cur.fetchone()
