from __future__ import annotations

from typing import Any


def query_example_page_total(cur: Any) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM example_table')
  return cur.fetchone()


def query_example_page_rows(cur: Any, *, size: int, offset: int) -> list[dict[str, Any]]:
  cur.execute(
    '''
    SELECT id, name, create_time, update_time
    FROM example_table
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (size, offset),
  )
  return cur.fetchall()


def insert_example_record(cur: Any, *, name: str) -> None:
  cur.execute(
    'INSERT INTO example_table(name) VALUES (?)',
    (name,),
  )
