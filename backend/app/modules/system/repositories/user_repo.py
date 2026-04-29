from __future__ import annotations

from typing import Any


def fetch_user_by_username(cur: Any, username: str) -> Any:
  cur.execute('SELECT * FROM users WHERE username = ?', (username,))
  return cur.fetchone()


def fetch_user_by_id(cur: Any, user_id: str) -> Any:
  cur.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
  return cur.fetchone()
