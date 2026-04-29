from __future__ import annotations

from typing import Any


def fetch_user_name_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT user_id, real_name, username FROM users')
  return cur.fetchall()
