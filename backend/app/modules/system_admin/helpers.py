from __future__ import annotations

from typing import Any, Callable


def query_value(query: Any, keys: list[str], default: str = '') -> str:
  for key in keys:
    value = query.get(key)
    if value is None:
      continue
    text = str(value).strip()
    if text:
      return text
  return default


def to_int(value: Any, default: int = 0) -> int:
  try:
    return int(str(value).strip())
  except (TypeError, ValueError):
    return default


def parse_dept_payload(payload: dict[str, Any], safe_int_func: Callable[[Any, int], int]) -> dict[str, Any]:
  sys_dept = payload.get('sysDept') if isinstance(payload, dict) else {}
  if not isinstance(sys_dept, dict):
    sys_dept = {}
  user_id_list = payload.get('userIdList') if isinstance(payload, dict) else []
  if not isinstance(user_id_list, list):
    user_id_list = []

  return {
    'dept_id': str(sys_dept.get('deptId', '') or '').strip(),
    'name': str(sys_dept.get('name', '')).strip(),
    'parent_id': str(sys_dept.get('parentId', '0') or '0').strip(),
    'sort_order': safe_int_func(sys_dept.get('sortOrder'), 0),
    'enabled': 1 if safe_int_func(sys_dept.get('enabled'), 0) == 1 else 0,
    'user_id_list': user_id_list,
  }


def parse_role_payload(payload: dict[str, Any]) -> dict[str, str]:
  return {
    'role_id': str(payload.get('roleId', '')).strip(),
    'role_name': str(payload.get('roleName', '')).strip(),
    'role_code': str(payload.get('roleCode', '')).strip(),
    'role_desc': str(payload.get('roleDesc', '')).strip(),
  }


def parse_role_menu_payload(payload: dict[str, Any]) -> dict[str, Any]:
  role_id = str(payload.get('roleId', '')).strip()
  menu_ids = str(payload.get('menuIds', '')).strip()
  return {
    'role_id': role_id,
    'menu_ids': [menu_id.strip() for menu_id in menu_ids.split(',') if menu_id.strip()],
  }


def parse_user_create_payload(payload: dict[str, Any]) -> dict[str, str]:
  role_value = payload.get('role') or []
  role_id = '2'
  if isinstance(role_value, list) and role_value:
    role_id = str(role_value[0])
  elif isinstance(role_value, str):
    role_id = role_value

  return {
    'username': str(payload.get('username', '')).strip(),
    'real_name': str(payload.get('realName', '')).strip(),
    'raw_password': str(payload.get('password', '')).strip() or '123456',
    'phone': str(payload.get('phone', '')).strip(),
    'email': str(payload.get('email', '')).strip(),
    'role_id': role_id,
  }


def parse_user_update_payload(payload: dict[str, Any]) -> dict[str, Any]:
  role_value = payload.get('role') or []
  role_id = None
  if isinstance(role_value, list) and role_value:
    role_id = str(role_value[0])
  elif isinstance(role_value, str) and role_value.strip():
    role_id = role_value.strip()

  return {
    'user_id': str(payload.get('userId', '')).strip(),
    'real_name': str(payload.get('realName', '')).strip(),
    'phone': str(payload.get('phone', '')).strip(),
    'email': str(payload.get('email', '')).strip(),
    'role_id': role_id,
  }
