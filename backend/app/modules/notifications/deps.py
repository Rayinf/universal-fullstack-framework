from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from fastapi import Request


@dataclass(frozen=True)
class NotificationRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  fail_func: Callable[[str, int], Any]
  get_conn_func: Callable[[], Any]
  get_current_user_func: Callable[[Request], Any]
  safe_int_func: Callable[[Any, int], int]
