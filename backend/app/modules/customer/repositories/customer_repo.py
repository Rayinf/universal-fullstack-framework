from __future__ import annotations

from typing import Any


def query_customer_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM customers {where_sql}', values)
  return cur.fetchone()


def query_customer_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, customer_code, customer_name, account_manager_name, introducer_name,
           customer_level, special_notes, creator, create_time, update_time
    FROM customers
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_customer_list_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT id, customer_code, customer_name, account_manager_name, introducer_name,
           customer_level, special_notes, creator, create_time, update_time
    FROM customers
    ORDER BY customer_code ASC
    ''',
  )
  return cur.fetchall()


def fetch_customer_by_id(cur: Any, customer_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, customer_code, customer_name, account_manager_name, introducer_name,
           customer_level, special_notes, creator, create_time, update_time
    FROM customers
    WHERE id = ?
    ''',
    (customer_id,),
  )
  return cur.fetchone()


def fetch_customer_id(cur: Any, customer_id: str) -> Any:
  cur.execute('SELECT id FROM customers WHERE id = ?', (customer_id,))
  return cur.fetchone()


def fetch_customer_id_by_code_excluding_id(cur: Any, customer_code: str, customer_id: str) -> Any:
  cur.execute('SELECT id FROM customers WHERE customer_code = ? AND id <> ?', (customer_code, customer_id))
  return cur.fetchone()


def insert_customer(
  cur: Any,
  *,
  customer_id: str,
  customer_code: str,
  customer_name: str,
  account_manager_name: str,
  introducer_name: str,
  customer_level: int,
  special_notes: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO customers(
      id, customer_code, customer_name, account_manager_name, introducer_name,
      customer_level, special_notes, creator, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, '系统管理员', ?, ?)
    ''',
    (
      customer_id,
      customer_code,
      customer_name,
      account_manager_name,
      introducer_name,
      customer_level,
      special_notes,
      now,
      now,
    ),
  )


def update_customer(
  cur: Any,
  *,
  customer_id: str,
  customer_code: str,
  customer_name: str,
  account_manager_name: str,
  introducer_name: str,
  customer_level: int,
  special_notes: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE customers
    SET customer_code = ?, customer_name = ?, account_manager_name = ?, introducer_name = ?,
        customer_level = ?, special_notes = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      customer_code,
      customer_name,
      account_manager_name,
      introducer_name,
      customer_level,
      special_notes,
      now,
      customer_id,
    ),
  )


def delete_customer(cur: Any, customer_id: str) -> None:
  cur.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
