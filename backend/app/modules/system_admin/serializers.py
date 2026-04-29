from __future__ import annotations

from typing import Any


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': (total + size - 1) // size if size > 0 else 0,
  }


def dept_row_to_dict(row: Any) -> dict[str, Any]:
  return {
    'deptId': str(row['dept_id']),
    'name': row['name'],
    'parentId': str(row['parent_id'] or '0'),
    'sortOrder': int(row['sort_order'] or 0),
    'enabled': int(row['enabled'] or 0),
    'tenantCode': 'LOCAL',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def dept_tree_user_to_dict(row: Any) -> dict[str, Any]:
  dept_id = str(row['dept_id'] or '0')
  return {
    'userId': str(row['user_id']),
    'username': row['username'],
    'realName': row['real_name'],
    'phone': row['phone'] or '',
    'email': row['email'] or '',
    'enabled': int(row['enabled'] or 0),
    'deptId': dept_id,
    'type': '1',
  }


def dept_detail_user_to_dict(row: Any) -> dict[str, Any]:
  return {
    'userId': str(row['user_id']),
    'username': row['username'],
    'realName': row['real_name'],
    'phone': row['phone'] or '',
    'email': row['email'] or '',
    'deptId': str(row['dept_id'] or ''),
    'enabled': int(row['enabled'] or 0),
    'tenantCode': 'LOCAL',
    'region': '0000',
  }


def build_dept_tree_node(dept_info: dict[str, Any], user_list: list[dict[str, Any]]) -> dict[str, Any]:
  return {
    'id': dept_info['deptId'],
    'name': dept_info['name'],
    'parentId': dept_info['parentId'],
    'type': '0',
    'deptInfo': dept_info,
    'children': [],
    'userList': user_list,
  }


def dept_page_row_to_dict(row: Any, dept_name_map: dict[str, str]) -> dict[str, Any]:
  parent_key = str(row['parent_id'] or '0')
  return {
    'deptId': str(row['dept_id']),
    'name': row['name'],
    'parentId': parent_key,
    'parentName': dept_name_map.get(parent_key, ''),
    'sortOrder': int(row['sort_order'] or 0),
    'enabled': int(row['enabled'] or 0),
    'tenantCode': 'LOCAL',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def dept_detail_to_dict(
  dept_row: Any,
  dept_name_map: dict[str, str],
  child_dept_count: int,
  user_list: list[dict[str, Any]],
) -> dict[str, Any]:
  parent_id = str(dept_row['parent_id'] or '0')
  return {
    'deptId': str(dept_row['dept_id']),
    'name': dept_row['name'],
    'parentId': parent_id,
    'parentName': dept_name_map.get(parent_id, '无'),
    'sortOrder': int(dept_row['sort_order'] or 0),
    'enabled': int(dept_row['enabled'] or 0),
    'tenantCode': 'LOCAL',
    'createTime': dept_row['create_time'] or '',
    'updateTime': dept_row['update_time'] or '',
    'userCount': len(user_list),
    'childDeptCount': child_dept_count,
    'userList': user_list,
  }


def role_to_dict(row: Any) -> dict[str, Any]:
  return {
    'roleId': str(row['role_id']),
    'roleName': row['role_name'],
    'roleCode': row['role_code'] or '',
    'roleDesc': row['role_desc'] or '',
    'delFlag': row['del_flag'] or '0',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def user_list_row_to_dict(row: Any) -> dict[str, Any]:
  return {
    'userId': str(row['user_id']),
    'username': row['username'],
    'realName': row['real_name'],
    'phone': row['phone'] or '',
    'email': row['email'] or '',
    'enabled': int(row['enabled'] or 0),
    'roleId': str(row['role_id'] or ''),
    'roleList': [
      {
        'roleId': str(row['role_id'] or ''),
        'roleName': row['role_name'] or '未分配角色',
      },
    ],
    'updateTime': row['update_time'] or '',
  }


def user_brief_to_dict(row: Any) -> dict[str, Any]:
  return {
    'userId': str(row['user_id']),
    'username': row['username'],
    'realName': row['real_name'],
  }


def user_detail_to_dict(row: Any) -> dict[str, Any]:
  return {
    'userId': str(row['user_id']),
    'username': row['username'],
    'realName': row['real_name'],
    'phone': row['phone'] or '',
    'email': row['email'] or '',
    'enabled': int(row['enabled'] or 0),
    'deptId': str(row['dept_id'] or '1'),
    'role': [str(row['role_id'] or '')],
    'roleList': [
      {
        'roleId': str(row['role_id'] or ''),
        'roleName': row['role_name'] or '未分配角色',
      },
    ],
  }


def user_info_to_dict(user: Any, dept_name: str) -> dict[str, Any]:
  return {
    'sysUser': {
      'userId': str(user['user_id']),
      'username': user['username'],
      'phone': user['phone'] or '',
      'email': user['email'] or '',
      'avatar': None,
      'deptId': str(user['dept_id'] or '1'),
      'realName': user['real_name'],
      'tenantCode': 'LOCAL',
      'region': '0000',
    },
    'deptName': dept_name,
    'roles': [str(user['role_id'] or '2')],
    'permissions': ['*:*:*'],
  }
