from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class AuthRouterDeps:
  fail_func: Callable[[str, int], Any]
  ok_func: Callable[[Any, str], dict[str, Any]]
  get_conn_func: Callable[[], Any]
  verify_password_func: Callable[[str, str], bool]
  build_token_func: Callable[[str, str, int], str]
  parse_token_func: Callable[..., dict[str, Any] | None]
  access_token_expire_seconds: int
  refresh_token_expire_seconds: int


@dataclass(frozen=True)
class SystemConfigRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  fail_func: Callable[[str, int], Any]
  get_conn_func: Callable[[], Any]


@dataclass(frozen=True)
class SystemRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  db_driver: str
