from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.notifications.deps import NotificationRouterDeps
from app.modules.notifications.services.errors import NotificationServiceError
from app.modules.notifications.services.notification_command_service import (
  delete_notification as delete_notification_command,
  mark_all_notifications_read as mark_all_notifications_read_command,
  mark_notification_read as mark_notification_read_command,
)
from app.modules.notifications.services.notification_query_service import (
  get_unread_count as get_unread_count_query,
  query_notification_page,
)


def register_notification_routes(router: APIRouter, deps: NotificationRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/local/notifications/page')
  def page_notifications(request: Request) -> dict[str, Any] | Any:
    try:
      return ok_func(query_notification_page(deps, request), 'success')
    except NotificationServiceError as error:
      return fail_func(error.message, error.code)

  @router.get('/local/notifications/unread-count')
  def get_unread_count(request: Request) -> dict[str, Any] | Any:
    try:
      return ok_func(get_unread_count_query(deps, request), 'success')
    except NotificationServiceError as error:
      return fail_func(error.message, error.code)

  @router.put('/local/notifications/{notification_id}/read')
  def mark_notification_read(notification_id: str, request: Request) -> dict[str, Any] | Any:
    try:
      mark_notification_read_command(deps, request, notification_id=notification_id)
    except NotificationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/local/notifications/read-all')
  def mark_all_notifications_read(request: Request) -> dict[str, Any] | Any:
    try:
      mark_all_notifications_read_command(deps, request)
    except NotificationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/notifications/{notification_id}')
  def delete_notification(notification_id: str, request: Request) -> dict[str, Any] | Any:
    try:
      delete_notification_command(deps, request, notification_id=notification_id)
    except NotificationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
