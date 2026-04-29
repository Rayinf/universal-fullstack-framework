from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request

from app.modules.notifications.deps import NotificationRouterDeps
from app.modules.notifications.routes.notification_routes import register_notification_routes


def create_notification_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  get_current_user_func: Callable[[Request], Any],
  safe_int_func: Callable[[Any, int], int],
) -> APIRouter:
  router = APIRouter(tags=['本地示例通知'])
  deps = NotificationRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    get_current_user_func=get_current_user_func,
    safe_int_func=safe_int_func,
  )
  register_notification_routes(router, deps)
  return router
