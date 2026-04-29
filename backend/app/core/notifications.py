from __future__ import annotations

import uuid
from typing import Any, Callable


def create_notification(
  user_id: str,
  title: str,
  content: str = '',
  ntype: int = 3,
  biz_type: str = '',
  biz_id: str = '',
  *,
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
) -> None:
  try:
    conn = get_conn_func()
    cur = conn.cursor()
    cur.execute(
      '''
      INSERT INTO notifications(id, user_id, title, content, type, biz_type, biz_id, is_read, create_time)
      VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
      ''',
      (str(uuid.uuid4()), user_id, title, content, ntype, biz_type, biz_id, now_str_func()),
    )
    conn.commit()
    conn.close()
  except Exception as exc:
    print(f'create_notification error: {exc}')


def create_notification_for_users(
  user_ids: list[str],
  title: str,
  content: str = '',
  ntype: int = 3,
  biz_type: str = '',
  biz_id: str = '',
  *,
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
) -> None:
  for uid in user_ids:
    create_notification(
      uid,
      title,
      content,
      ntype,
      biz_type,
      biz_id,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
    )
