from __future__ import annotations

from typing import Any, Callable

from app.bootstrap.init_db_seed_demo_common import seed_demo_common_data
from app.bootstrap.init_db_seed_production import seed_production_data
from app.bootstrap.init_db_seed_sales import seed_sales_data
from app.bootstrap.init_db_seed_system import seed_system_data


def seed_bootstrap_data(
  cur: Any,
  *,
  now_str: Callable[[], str],
  safe_int: Callable[[Any, int], int],
  hash_password: Callable[[str], str],
  is_password_hashed: Callable[[str], bool],
  menu_tree: Callable[[], list[dict[str, Any]]],
  flatten_menu_ids: Callable[[list[dict[str, Any]]], list[str]],
) -> None:
  seed_system_data(
    cur,
    now_str=now_str,
    hash_password=hash_password,
    is_password_hashed=is_password_hashed,
    menu_tree=menu_tree,
    flatten_menu_ids=flatten_menu_ids,
  )
  seed_demo_common_data(cur, now_str=now_str)
  seed_sales_data(cur, now_str=now_str)
  seed_production_data(cur, now_str=now_str, safe_int=safe_int)
