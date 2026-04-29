from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, Request

from app.modules.attachments.deps import AttachmentRouterDeps
from app.modules.attachments.routes.attachment_routes import register_attachment_routes


def create_attachment_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  get_current_user_func: Callable[[Request], Any],
  now_str_func: Callable[[], str],
  uploads_dir: Path,
) -> APIRouter:
  router = APIRouter(tags=['本地示例附件'])
  deps = AttachmentRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    get_current_user_func=get_current_user_func,
    now_str_func=now_str_func,
    uploads_dir=uploads_dir,
  )
  register_attachment_routes(router, deps)
  return router
