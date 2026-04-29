from __future__ import annotations

from typing import Any


def query_role_menu_rows(cur: Any, role_id: str) -> list[Any]:
  cur.execute('SELECT menu_id FROM role_menus WHERE role_id = ? ORDER BY menu_id ASC', (role_id,))
  return cur.fetchall()
