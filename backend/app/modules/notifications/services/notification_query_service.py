from __future__ import annotations

from fastapi import Request

from app.modules.notifications.deps import NotificationRouterDeps
from app.modules.notifications.helpers import build_notification_where, parse_notification_page_params, require_user_id
from app.modules.notifications.repositories.notification_repo import (
  query_notification_page_rows,
  query_notification_page_total,
  query_unread_count_row,
)
from app.modules.notifications.serializers import build_notification_page_result, notification_to_dict


def query_notification_page(deps: NotificationRouterDeps, request: Request) -> dict[str, object]:
  user_id = require_user_id(deps, request)
  current, size, is_read = parse_notification_page_params(request.query_params, deps.safe_int_func)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql, args = build_notification_where(user_id, is_read)
  total = int(query_notification_page_total(cur, where_sql, tuple(args))['cnt'])
  rows = query_notification_page_rows(cur, where_sql, tuple(args), size, (current - 1) * size)
  conn.close()

  return build_notification_page_result([notification_to_dict(row) for row in rows], total, current, size)


def get_unread_count(deps: NotificationRouterDeps, request: Request) -> dict[str, int]:
  user_id = require_user_id(deps, request)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  count = int(query_unread_count_row(cur, user_id)['cnt'])
  conn.close()
  return {'count': count}
