from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from fastapi import Request


@dataclass(frozen=True)
class SystemAdminRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  get_conn_func: Callable[[], Any]
  menu_tree_func: Callable[[], list[dict[str, Any]]]


@dataclass(frozen=True)
class DeptReadRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  fail_func: Callable[[str, int], Any]
  get_conn_func: Callable[[], Any]
  build_dept_tree_func: Callable[..., list[dict[str, Any]]]


@dataclass(frozen=True)
class DeptWriteRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  fail_func: Callable[[str, int], Any]
  get_conn_func: Callable[[], Any]
  safe_int_func: Callable[[Any, int], int]
  now_str_func: Callable[[], str]
  collect_descendant_ids_func: Callable[[str, list[Any]], set[str]]


@dataclass(frozen=True)
class RoleRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  fail_func: Callable[[str, int], Any]
  get_conn_func: Callable[[], Any]
  now_str_func: Callable[[], str]


@dataclass(frozen=True)
class UserRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  fail_func: Callable[[str, int], Any]
  get_conn_func: Callable[[], Any]
  now_str_func: Callable[[], str]
  hash_password_func: Callable[[str], str]
  get_current_user_func: Callable[[Request], Any]
