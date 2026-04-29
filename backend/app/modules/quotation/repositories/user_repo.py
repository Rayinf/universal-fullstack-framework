from __future__ import annotations

from typing import Any


def fetch_user_role_id(cur: Any, user_id: str) -> str:
  cur.execute('SELECT role_id FROM users WHERE user_id = ?', (user_id,))
  user_row = cur.fetchone()
  return str(user_row['role_id'] or '').strip() if user_row else ''


def fetch_user_ids_by_role(cur: Any, role_id: str) -> list[str]:
  cur.execute('SELECT user_id FROM users WHERE role_id = ?', (role_id,))
  return [str(row['user_id']) for row in cur.fetchall()]


def fetch_role_map(cur: Any) -> dict[str, str]:
  cur.execute('SELECT role_id, role_name FROM roles')
  return {str(row['role_id']): row['role_name'] or str(row['role_id']) for row in cur.fetchall()}


def fetch_user_name_map(cur: Any) -> dict[str, str]:
  cur.execute('SELECT user_id, real_name, username FROM users')
  return {
    str(row['user_id']): (row['real_name'] or row['username'] or str(row['user_id']))
    for row in cur.fetchall()
  }
