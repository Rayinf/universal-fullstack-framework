from __future__ import annotations

from typing import Any, Callable

from app.bootstrap.init_db_seed import seed_bootstrap_data
from app.bootstrap.init_db_schema import apply_bootstrap_schema


def init_db(
  *,
  get_conn: Callable[[], Any],
  now_str: Callable[[], str],
  safe_int: Callable[[Any, int], int],
  hash_password: Callable[[str], str],
  is_password_hashed: Callable[[str], bool],
  _sync_pg_serial_sequences: Callable[[Any], None],
  menu_tree: Callable[[], list[dict[str, Any]]],
  flatten_menu_ids: Callable[[list[dict[str, Any]]], list[str]],
) -> None:
  conn = get_conn()
  cur = conn.cursor()

  try:
    apply_bootstrap_schema(cur)
    seed_bootstrap_data(
      cur,
      now_str=now_str,
      safe_int=safe_int,
      hash_password=hash_password,
      is_password_hashed=is_password_hashed,
      menu_tree=menu_tree,
      flatten_menu_ids=flatten_menu_ids,
    )
    _sync_pg_serial_sequences(cur)
    conn.commit()
  finally:
    conn.close()
