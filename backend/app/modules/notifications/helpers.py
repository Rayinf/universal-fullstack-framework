from __future__ import annotations

from typing import Any, Callable

from fastapi import Request

from app.modules.notifications.deps import NotificationRouterDeps
from app.modules.notifications.services.errors import NotificationServiceError


def require_user_id(deps: NotificationRouterDeps, request: Request) -> str:
  user = deps.get_current_user_func(request)
  if not user:
    raise NotificationServiceError('未登录', 401)
  return str(user['user_id'])


def parse_notification_page_params(
  query_params: Any,
  safe_int_func: Callable[[Any, int], int],
) -> tuple[int, int, str]:
  params = dict(query_params)
  return (
    safe_int_func(params.get('current'), 1),
    safe_int_func(params.get('size'), 20),
    params.get('isRead', '').strip(),
  )


def build_notification_where(user_id: str, is_read: str) -> tuple[str, list[Any]]:
  where = 'WHERE user_id = ?'
  args: list[Any] = [user_id]
  if is_read in ('0', '1'):
    where += ' AND is_read = ?'
    args.append(int(is_read))
  return where, args
