from __future__ import annotations

from typing import Any


ROLE_SELECT_SQL = '''
SELECT role_id, role_name, role_code, role_desc, del_flag, create_time, update_time
FROM roles
'''


def query_role_list_rows(cur: Any) -> list[Any]:
  cur.execute(f'{ROLE_SELECT_SQL} ORDER BY role_id ASC')
  return cur.fetchall()


def query_role_page_total(cur: Any, where_sql: str, values: list[Any]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM roles {where_sql}', values)
  return cur.fetchone()


def query_role_page_rows(cur: Any, where_sql: str, values: list[Any], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    {ROLE_SELECT_SQL}
    {where_sql}
    ORDER BY role_id ASC
    LIMIT ? OFFSET ?
    ''',
    [*values, size, offset],
  )
  return cur.fetchall()


def fetch_role_by_id(cur: Any, role_id: str) -> Any:
  cur.execute(f'{ROLE_SELECT_SQL} WHERE role_id = ?', (role_id,))
  return cur.fetchone()


def fetch_role_by_name_or_code(cur: Any, role_name: str, role_code: str) -> Any:
  cur.execute('SELECT role_id FROM roles WHERE role_name = ? OR role_code = ?', (role_name, role_code))
  return cur.fetchone()


def fetch_other_role_by_name_or_code(cur: Any, role_id: str, role_name: str, role_code: str) -> Any:
  cur.execute(
    'SELECT role_id FROM roles WHERE role_id <> ? AND (role_name = ? OR role_code = ?)',
    (role_id, role_name, role_code),
  )
  return cur.fetchone()


def insert_role(cur: Any, *, role_id: str, role_name: str, role_code: str, role_desc: str, now: str) -> None:
  cur.execute(
    '''
    INSERT INTO roles(role_id, role_name, role_code, role_desc, del_flag, create_time, update_time)
    VALUES (?, ?, ?, ?, '0', ?, ?)
    ''',
    (role_id, role_name, role_code, role_desc, now, now),
  )


def update_role(cur: Any, *, role_id: str, role_name: str, role_code: str, role_desc: str, now: str) -> None:
  cur.execute(
    '''
    UPDATE roles
    SET role_name = ?, role_code = ?, role_desc = ?, update_time = ?
    WHERE role_id = ?
    ''',
    (role_name, role_code, role_desc, now, role_id),
  )


def count_users_by_role(cur: Any, role_id: str) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM users WHERE role_id = ?', (role_id,))
  return cur.fetchone()


def delete_role_menus(cur: Any, role_id: str) -> None:
  cur.execute('DELETE FROM role_menus WHERE role_id = ?', (role_id,))


def delete_role(cur: Any, role_id: str) -> None:
  cur.execute('DELETE FROM roles WHERE role_id = ?', (role_id,))


def insert_role_menus(cur: Any, role_id: str, menu_ids: list[str]) -> None:
  cur.executemany(
    'INSERT INTO role_menus(role_id, menu_id) VALUES (?, ?)',
    [(role_id, menu_id) for menu_id in menu_ids],
  )


def query_user_ids_by_role(cur: Any, role_id: str) -> list[Any]:
  cur.execute('SELECT user_id FROM users WHERE role_id = ? ORDER BY user_id ASC', (role_id,))
  return cur.fetchall()
