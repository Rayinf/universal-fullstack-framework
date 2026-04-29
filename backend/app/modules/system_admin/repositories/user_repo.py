from __future__ import annotations

from typing import Any


def fetch_dept_name(cur: Any, dept_id: str) -> Any:
  cur.execute('SELECT name FROM depts WHERE dept_id = ?', (dept_id,))
  return cur.fetchone()


def query_all_user_brief_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT user_id, username, real_name FROM users ORDER BY user_id ASC')
  return cur.fetchall()


def query_user_page_total(cur: Any, where_sql: str, values: list[Any]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM users {where_sql}', values)
  return cur.fetchone()


def query_user_page_rows(cur: Any, where_sql: str, values: list[Any], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT u.user_id, u.username, u.real_name, u.phone, u.email, u.enabled, u.role_id, u.update_time, r.role_name
    FROM users u
    LEFT JOIN roles r ON u.role_id = r.role_id
    {where_sql}
    ORDER BY u.update_time DESC
    LIMIT ? OFFSET ?
    ''',
    [*values, size, offset],
  )
  return cur.fetchall()


def fetch_user_detail_row(cur: Any, user_id: str) -> Any:
  cur.execute(
    '''
    SELECT u.user_id, u.username, u.real_name, u.phone, u.email, u.enabled, u.role_id, u.dept_id, r.role_name
    FROM users u
    LEFT JOIN roles r ON u.role_id = r.role_id
    WHERE u.user_id = ?
    ''',
    (user_id,),
  )
  return cur.fetchone()


def insert_user(
  cur: Any,
  *,
  user_id: str,
  username: str,
  password: str,
  real_name: str,
  phone: str,
  email: str,
  role_id: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO users(user_id, username, password, real_name, phone, email, enabled, role_id, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
    ''',
    (user_id, username, password, real_name, phone, email, role_id, now, now),
  )


def fetch_user_by_id(cur: Any, user_id: str) -> Any:
  cur.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
  return cur.fetchone()


def update_user(cur: Any, fields: list[str], values: list[Any], user_id: str) -> None:
  cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", [*values, user_id])


def update_user_password(cur: Any, password: str, now: str, user_id: str) -> None:
  cur.execute(
    'UPDATE users SET password = ?, update_time = ? WHERE user_id = ?',
    (password, now, user_id),
  )


def update_user_base_info(cur: Any, real_name: str, phone: str, email: str, now: str, user_id: str) -> None:
  cur.execute(
    'UPDATE users SET real_name = ?, phone = ?, email = ?, update_time = ? WHERE user_id = ?',
    (real_name, phone, email, now, user_id),
  )


def delete_user(cur: Any, user_id: str) -> None:
  cur.execute('DELETE FROM users WHERE user_id = ?', (user_id,))


def update_user_enabled(cur: Any, enabled: int, now: str, user_id: str) -> None:
  cur.execute('UPDATE users SET enabled = ?, update_time = ? WHERE user_id = ?', (enabled, now, user_id))
