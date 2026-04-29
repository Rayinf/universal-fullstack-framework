from __future__ import annotations

from typing import Any


def query_tree_dept_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT dept_id, name, parent_id, sort_order, enabled, create_time, update_time
    FROM depts
    ORDER BY sort_order ASC, create_time ASC
    ''',
  )
  return cur.fetchall()


def query_tree_user_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT user_id, username, real_name, phone, email, enabled, dept_id
    FROM users
    ORDER BY user_id ASC
    ''',
  )
  return cur.fetchall()


def query_dept_page_total(cur: Any, where_sql: str, values: list[Any]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM depts {where_sql}', values)
  return cur.fetchone()


def query_dept_page_rows(cur: Any, where_sql: str, values: list[Any], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT dept_id, name, parent_id, sort_order, enabled, create_time, update_time
    FROM depts
    {where_sql}
    ORDER BY sort_order ASC, create_time ASC
    LIMIT ? OFFSET ?
    ''',
    [*values, size, offset],
  )
  return cur.fetchall()


def query_dept_name_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT dept_id, name FROM depts')
  return cur.fetchall()


def fetch_dept_by_name(cur: Any, dept_name: str) -> Any:
  cur.execute(
    '''
    SELECT dept_id, name, parent_id, sort_order, enabled, create_time, update_time
    FROM depts
    WHERE name = ?
    ''',
    (dept_name,),
  )
  return cur.fetchone()


def fetch_dept_by_id(cur: Any, dept_id: str) -> Any:
  cur.execute(
    '''
    SELECT dept_id, name, parent_id, sort_order, enabled, create_time, update_time
    FROM depts
    WHERE dept_id = ?
    ''',
    (dept_id,),
  )
  return cur.fetchone()


def query_child_dept_count(cur: Any, dept_id: str) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM depts WHERE parent_id = ?', (dept_id,))
  return cur.fetchone()


def query_dept_user_rows(cur: Any, dept_id: str) -> list[Any]:
  cur.execute(
    '''
    SELECT user_id, username, real_name, phone, email, enabled, dept_id
    FROM users
    WHERE dept_id = ?
    ORDER BY user_id ASC
    ''',
    (dept_id,),
  )
  return cur.fetchall()


def query_all_dept_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT dept_id, parent_id FROM depts')
  return cur.fetchall()


def fetch_parent_dept(cur: Any, parent_id: str) -> Any:
  cur.execute('SELECT dept_id FROM depts WHERE dept_id = ?', (parent_id,))
  return cur.fetchone()


def fetch_other_dept_by_name(cur: Any, dept_name: str, dept_id: str) -> Any:
  cur.execute('SELECT dept_id FROM depts WHERE name = ? AND dept_id <> ?', (dept_name, dept_id))
  return cur.fetchone()


def insert_dept(
  cur: Any,
  *,
  dept_id: str,
  name: str,
  parent_id: str,
  sort_order: int,
  enabled: int,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO depts(dept_id, name, parent_id, sort_order, enabled, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',
    (dept_id, name, parent_id, sort_order, enabled, now, now),
  )


def update_dept(
  cur: Any,
  *,
  dept_id: str,
  name: str,
  parent_id: str,
  sort_order: int,
  enabled: int,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE depts
    SET name = ?, parent_id = ?, sort_order = ?, enabled = ?, update_time = ?
    WHERE dept_id = ?
    ''',
    (name, parent_id, sort_order, enabled, now, dept_id),
  )


def reset_dept_users(cur: Any, dept_id: str, now: str) -> None:
  cur.execute('UPDATE users SET dept_id = ?, update_time = ? WHERE dept_id = ?', ('1', now, dept_id))


def assign_users_to_dept(cur: Any, dept_id: str, now: str, user_id_list: list[Any]) -> None:
  placeholders = ','.join(['?'] * len(user_id_list))
  cur.execute(
    f'UPDATE users SET dept_id = ?, update_time = ? WHERE user_id IN ({placeholders})',
    [dept_id, now, *[str(user_id) for user_id in user_id_list]],
  )


def delete_dept(cur: Any, dept_id: str) -> None:
  cur.execute('DELETE FROM depts WHERE dept_id = ?', (dept_id,))


def update_dept_enabled(cur: Any, dept_id: str, enabled: int, now: str) -> None:
  cur.execute('UPDATE depts SET enabled = ?, update_time = ? WHERE dept_id = ?', (enabled, now, dept_id))
