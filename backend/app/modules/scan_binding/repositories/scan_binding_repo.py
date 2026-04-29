from __future__ import annotations

from typing import Any


def query_scan_binding_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM scan_binding_processes {where_sql}', values)
  return cur.fetchone()


def query_scan_binding_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, scan_asset_number, identifier, process_id, create_time, update_time
    FROM scan_binding_processes
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    [*values, size, offset],
  )
  return cur.fetchall()


def query_process_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT id, name FROM basic_infos WHERE type = 8')
  return cur.fetchall()


def insert_scan_binding_process(
  cur: Any,
  *,
  scan_asset_number: str,
  identifier: str,
  process_id: int,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO scan_binding_processes(scan_asset_number, identifier, process_id, create_time, update_time)
    VALUES (?, ?, ?, ?, ?)
    ''',
    (scan_asset_number, identifier, process_id, now, now),
  )


def fetch_scan_binding_by_id(cur: Any, record_id: int) -> Any:
  cur.execute('SELECT id FROM scan_binding_processes WHERE id = ?', (record_id,))
  return cur.fetchone()


def update_scan_binding_process(
  cur: Any,
  *,
  record_id: int,
  scan_asset_number: str,
  identifier: str,
  process_id: int,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE scan_binding_processes
    SET scan_asset_number = ?, identifier = ?, process_id = ?, update_time = ?
    WHERE id = ?
    ''',
    (scan_asset_number, identifier, process_id, now, record_id),
  )


def delete_scan_binding_process(cur: Any, record_id: int) -> None:
  cur.execute('DELETE FROM scan_binding_processes WHERE id = ?', (int(record_id),))
