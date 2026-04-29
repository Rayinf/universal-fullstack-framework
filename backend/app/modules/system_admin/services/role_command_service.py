from __future__ import annotations

import uuid

from app.modules.system_admin.deps import RoleRouterDeps
from app.modules.system_admin.repositories.role_repo import (
  count_users_by_role,
  delete_role,
  delete_role_menus,
  fetch_other_role_by_name_or_code,
  fetch_role_by_id,
  fetch_role_by_name_or_code,
  insert_role,
  insert_role_menus,
  update_role,
)
from app.modules.system_admin.services.errors import SystemAdminServiceError


def create_role_record(deps: RoleRouterDeps, *, role_name: str, role_code: str, role_desc: str) -> None:
  if not role_name or not role_code:
    raise SystemAdminServiceError('角色名称和角色标识不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if fetch_role_by_name_or_code(cur, role_name, role_code):
    conn.close()
    raise SystemAdminServiceError('角色名称或角色标识已存在', 400)

  insert_role(
    cur,
    role_id=str(uuid.uuid4()),
    role_name=role_name,
    role_code=role_code,
    role_desc=role_desc,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()


def update_role_record(
  deps: RoleRouterDeps,
  *,
  role_id: str,
  role_name: str,
  role_code: str,
  role_desc: str,
) -> None:
  if not role_id:
    raise SystemAdminServiceError('roleId不能为空', 400)
  if not role_name or not role_code:
    raise SystemAdminServiceError('角色名称和角色标识不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_role_by_id(cur, role_id):
    conn.close()
    raise SystemAdminServiceError('角色不存在', 404)

  if fetch_other_role_by_name_or_code(cur, role_id, role_name, role_code):
    conn.close()
    raise SystemAdminServiceError('角色名称或角色标识已存在', 400)

  update_role(
    cur,
    role_id=role_id,
    role_name=role_name,
    role_code=role_code,
    role_desc=role_desc,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()


def delete_role_record(deps: RoleRouterDeps, *, role_id: str) -> None:
  if role_id == '1':
    raise SystemAdminServiceError('系统管理员角色不可删除', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_role_by_id(cur, role_id):
    conn.close()
    raise SystemAdminServiceError('角色不存在', 404)

  if int(count_users_by_role(cur, role_id)['cnt']) > 0:
    conn.close()
    raise SystemAdminServiceError('该角色下仍有用户，无法删除', 400)

  delete_role_menus(cur, role_id)
  delete_role(cur, role_id)
  conn.commit()
  conn.close()


def update_role_menu_record(deps: RoleRouterDeps, *, role_id: str, menu_ids: list[str]) -> None:
  if not role_id:
    raise SystemAdminServiceError('roleId不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_role_by_id(cur, role_id):
    conn.close()
    raise SystemAdminServiceError('角色不存在', 404)

  delete_role_menus(cur, role_id)
  if menu_ids:
    insert_role_menus(cur, role_id, menu_ids)
  conn.commit()
  conn.close()
