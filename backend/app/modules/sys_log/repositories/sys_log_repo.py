from __future__ import annotations

from typing import Any


def query_sys_log_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM sys_log_users {where_sql}', values)
  return cur.fetchone()


def query_sys_log_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, type, content, sys_log_id, creator, create_by, real_name, create_time, update_time, tenant_code
    FROM sys_log_users
    {where_sql}
    ORDER BY create_time DESC, id DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def delete_sys_logs_by_ids(cur: Any, id_list: list[str]) -> None:
  placeholders = ','.join(['?'] * len(id_list))
  cur.execute(f'DELETE FROM sys_log_users WHERE id IN ({placeholders})', tuple(id_list))


def clear_sys_logs_by_type(cur: Any, log_type: int) -> None:
  cur.execute('DELETE FROM sys_log_users WHERE type = ?', (log_type,))


def clear_sys_logs_by_type_with_cutoff(cur: Any, log_type: int, cutoff: str) -> None:
  cur.execute('DELETE FROM sys_log_users WHERE type = ? AND create_time >= ?', (log_type, cutoff))


def query_sys_log_export_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT id, type, content, creator, real_name, create_time
    FROM sys_log_users
    ORDER BY create_time DESC, id DESC
    ''',
    (),
  )
  return cur.fetchall()


def fetch_sys_log_detail(cur: Any, log_id: int) -> Any:
  cur.execute(
    '''
    SELECT id, type, content, sys_log_id, creator, create_by, real_name, create_time, update_time, tenant_code
    FROM sys_log_users
    WHERE id = ?
    ''',
    (log_id,),
  )
  return cur.fetchone()
