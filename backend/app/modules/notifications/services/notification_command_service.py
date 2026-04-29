from __future__ import annotations

from fastapi import Request

from app.modules.notifications.deps import NotificationRouterDeps
from app.modules.notifications.helpers import require_user_id
from app.modules.notifications.repositories.notification_repo import (
  delete_notification as delete_notification_row,
  mark_all_notifications_read as mark_all_notifications_read_row,
  mark_notification_read as mark_notification_read_row,
)


def mark_notification_read(deps: NotificationRouterDeps, request: Request, *, notification_id: str) -> bool:
  user_id = require_user_id(deps, request)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  mark_notification_read_row(cur, notification_id, user_id)
  conn.commit()
  conn.close()
  return True


def mark_all_notifications_read(deps: NotificationRouterDeps, request: Request) -> bool:
  user_id = require_user_id(deps, request)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  mark_all_notifications_read_row(cur, user_id)
  conn.commit()
  conn.close()
  return True


def delete_notification(deps: NotificationRouterDeps, request: Request, *, notification_id: str) -> bool:
  user_id = require_user_id(deps, request)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_notification_row(cur, notification_id, user_id)
  conn.commit()
  conn.close()
  return True
