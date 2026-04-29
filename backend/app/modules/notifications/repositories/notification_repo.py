from __future__ import annotations

from typing import Any


def query_notification_page_total(cur: Any, where_sql: str, args: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM notifications {where_sql}', args)
  return cur.fetchone()


def query_notification_page_rows(cur: Any, where_sql: str, args: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, user_id, title, content, type, biz_type, biz_id, is_read, create_time
    FROM notifications {where_sql}
    ORDER BY create_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*args, size, offset),
  )
  return cur.fetchall()


def query_unread_count_row(cur: Any, user_id: str) -> Any:
  cur.execute('SELECT COUNT(1) AS cnt FROM notifications WHERE user_id = ? AND is_read = 0', (user_id,))
  return cur.fetchone()


def mark_notification_read(cur: Any, notification_id: str, user_id: str) -> None:
  cur.execute('UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?', (notification_id, user_id))


def mark_all_notifications_read(cur: Any, user_id: str) -> None:
  cur.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0', (user_id,))


def delete_notification(cur: Any, notification_id: str, user_id: str) -> None:
  cur.execute('DELETE FROM notifications WHERE id = ? AND user_id = ?', (notification_id, user_id))
