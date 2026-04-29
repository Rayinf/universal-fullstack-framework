from __future__ import annotations

from typing import Any


def query_basic_info_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM basic_infos {where_sql}', values)
  return cur.fetchone()


def query_basic_info_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, name, type, parent_id, create_time, update_time
    FROM basic_infos
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_basic_info_list_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT id, name, type, parent_id, create_time, update_time FROM basic_infos ORDER BY id ASC')
  return cur.fetchall()


def query_basic_info_list_rows_by_type(cur: Any, info_type: int) -> list[Any]:
  cur.execute(
    'SELECT id, name, type, parent_id, create_time, update_time FROM basic_infos WHERE type = ? ORDER BY id ASC',
    (info_type,),
  )
  return cur.fetchall()


def fetch_basic_info_by_type_and_name(cur: Any, info_type: int, name: str) -> Any:
  cur.execute('SELECT id FROM basic_infos WHERE type = ? AND name = ?', (info_type, name))
  return cur.fetchone()


def fetch_basic_info_by_id(cur: Any, info_id: int) -> Any:
  cur.execute('SELECT id FROM basic_infos WHERE id = ?', (info_id,))
  return cur.fetchone()


def fetch_other_basic_info_by_type_and_name(cur: Any, info_type: int, name: str, info_id: int) -> Any:
  cur.execute('SELECT id FROM basic_infos WHERE type = ? AND name = ? AND id <> ?', (info_type, name, info_id))
  return cur.fetchone()


def insert_basic_info(cur: Any, *, name: str, info_type: int, parent_id: int | None, now: str) -> None:
  cur.execute(
    '''
    INSERT INTO basic_infos(name, type, parent_id, create_time, update_time)
    VALUES (?, ?, ?, ?, ?)
    ''',
    (name, info_type, parent_id, now, now),
  )


def update_basic_info(cur: Any, *, info_id: int, name: str, info_type: int, parent_id: int | None, now: str) -> None:
  cur.execute(
    '''
    UPDATE basic_infos
    SET name = ?, type = ?, parent_id = ?, update_time = ?
    WHERE id = ?
    ''',
    (name, info_type, parent_id, now, info_id),
  )


def delete_basic_info(cur: Any, info_id: int) -> None:
  cur.execute('DELETE FROM basic_infos WHERE id = ?', (info_id,))
