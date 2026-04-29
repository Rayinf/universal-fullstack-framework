from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from fastapi import Request


def now_str() -> str:
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def safe_int(value: Any, default: int = 0) -> int:
  try:
    return int(value)
  except (TypeError, ValueError):
    return default


def safe_float(value: Any, default: float = 0.0) -> float:
  try:
    return float(value)
  except (TypeError, ValueError):
    return default


def safe_datetime(value: str | None) -> datetime | None:
  if not value:
    return None
  for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
    try:
      return datetime.strptime(value, fmt)
    except ValueError:
      continue
  return None


def load_name_maps(cur: Any) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
  cur.execute('SELECT user_id, real_name, username FROM users')
  user_map = {
    str(row['user_id']): (row['real_name'] or row['username'] or str(row['user_id']))
    for row in cur.fetchall()
  }
  cur.execute('SELECT dept_id, name FROM depts')
  dept_map = {str(row['dept_id']): row['name'] for row in cur.fetchall()}
  cur.execute('SELECT id, workstation_name FROM workstations')
  workstation_map = {str(row['id']): row['workstation_name'] for row in cur.fetchall()}
  return user_map, dept_map, workstation_map


def create_get_current_user(
  get_conn_func: Callable[[], Any],
  parse_token_func: Callable[[str, str], dict[str, Any] | None],
) -> Callable[[Request], Any]:
  def get_current_user(request: Request) -> Any:
    user_id = str(getattr(request.state, 'user_id', '') or '').strip()
    if not user_id:
      auth_header = request.headers.get('Authorization', '')
      token = auth_header.replace('Bearer ', '').replace('bearer ', '').strip()
      if not token:
        return None
      payload = parse_token_func(token, expected_type='access')
      if not payload:
        return None
      user_id = str(payload.get('sub', '')).strip()
    if not user_id:
      return None

    conn = get_conn_func()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

  return get_current_user
