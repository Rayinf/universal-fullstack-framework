from __future__ import annotations

from typing import Any


def query_crud_item_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM crud_items {where_sql}', values)
  return cur.fetchone()


def query_crud_item_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, name, code, remark, status, create_time, update_time
    FROM crud_items
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def insert_crud_item(
  cur: Any,
  *,
  item_id: str,
  name: str,
  code: str,
  remark: str,
  status: int,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO crud_items(id, name, code, remark, status, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',
    (item_id, name, code, remark, status, now, now),
  )


def fetch_crud_item_id(cur: Any, item_id: str) -> Any:
  cur.execute('SELECT id FROM crud_items WHERE id = ?', (item_id,))
  return cur.fetchone()


def update_crud_item(
  cur: Any,
  *,
  item_id: str,
  name: str,
  code: str,
  remark: str,
  status: int,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE crud_items
    SET name = ?, code = ?, remark = ?, status = ?, update_time = ?
    WHERE id = ?
    ''',
    (name, code, remark, status, now, item_id),
  )


def delete_crud_item(cur: Any, item_id: str) -> None:
  cur.execute('DELETE FROM crud_items WHERE id = ?', (item_id,))
