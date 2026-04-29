from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from app.modules.system_admin.repositories.dept_repo import query_tree_dept_rows, query_tree_user_rows
from app.modules.system_admin.serializers import build_dept_tree_node, dept_row_to_dict, dept_tree_user_to_dict


def build_dept_tree(get_conn_func: Callable[[], Any], include_users: bool = True) -> list[dict[str, Any]]:
  conn = get_conn_func()
  cur = conn.cursor()
  dept_rows = query_tree_dept_rows(cur)

  user_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
  if include_users:
    for user_row in query_tree_user_rows(cur):
      dept_id = str(user_row['dept_id'] or '0')
      user_group[dept_id].append(dept_tree_user_to_dict(user_row))

  conn.close()

  node_map: dict[str, dict[str, Any]] = {}
  roots: list[dict[str, Any]] = []

  for row in dept_rows:
    dept_info = dept_row_to_dict(row)
    dept_id = dept_info['deptId']
    node_map[dept_id] = build_dept_tree_node(dept_info, user_group.get(dept_id, []))

  for node in node_map.values():
    parent_id = str(node['parentId'] or '0')
    parent_node = node_map.get(parent_id)
    if parent_id == '0' or not parent_node:
      roots.append(node)
    else:
      parent_node['children'].append(node)

  return roots


def collect_descendant_ids(dept_id: str, all_nodes: list[Any]) -> set[str]:
  children_map: dict[str, list[str]] = defaultdict(list)
  for row in all_nodes:
    children_map[str(row['parent_id'] or '0')].append(str(row['dept_id']))

  result: set[str] = set()
  stack = [dept_id]
  while stack:
    current = stack.pop()
    for child_id in children_map.get(current, []):
      if child_id not in result:
        result.add(child_id)
        stack.append(child_id)
  return result
