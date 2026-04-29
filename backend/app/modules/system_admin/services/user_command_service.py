from __future__ import annotations

import uuid
from typing import Any

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.system_admin.deps import UserRouterDeps
from app.modules.system_admin.repositories.user_repo import (
  delete_user,
  fetch_user_by_id,
  insert_user,
  update_user,
  update_user_base_info,
  update_user_enabled,
  update_user_password,
)
from app.modules.system_admin.services.errors import SystemAdminServiceError


def create_user_record(
  deps: UserRouterDeps,
  *,
  username: str,
  real_name: str,
  raw_password: str,
  phone: str,
  email: str,
  role_id: str,
) -> None:
  if not username or not real_name:
    raise SystemAdminServiceError('用户名和真实姓名不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    insert_user(
      cur,
      user_id=str(uuid.uuid4()),
      username=username,
      password=deps.hash_password_func(raw_password),
      real_name=real_name,
      phone=phone,
      email=email,
      role_id=role_id,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError:
    conn.rollback()
    conn.close()
    raise SystemAdminServiceError('用户名已存在', 400)
  conn.close()


def update_user_record(
  deps: UserRouterDeps,
  *,
  user_id: str,
  real_name: str,
  phone: str,
  email: str,
  role_id: str | None,
) -> None:
  if not user_id:
    raise SystemAdminServiceError('userId不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_user_by_id(cur, user_id):
    conn.close()
    raise SystemAdminServiceError('用户不存在', 404)

  fields = ['update_time = ?']
  values: list[Any] = [deps.now_str_func()]
  if real_name:
    fields.append('real_name = ?')
    values.append(real_name)
  fields.append('phone = ?')
  values.append(phone)
  fields.append('email = ?')
  values.append(email)
  if role_id is not None:
    fields.append('role_id = ?')
    values.append(role_id)
  update_user(cur, fields, values, user_id)
  conn.commit()
  conn.close()


def update_user_password_record(deps: UserRouterDeps, *, user_id: str, raw_password: str) -> None:
  if not user_id or not raw_password:
    raise SystemAdminServiceError('参数不完整', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_user_password(cur, deps.hash_password_func(raw_password), deps.now_str_func(), user_id)
  conn.commit()
  conn.close()


def update_user_base_info_record(
  deps: UserRouterDeps,
  *,
  user_id: str,
  real_name: str,
  phone: str,
  email: str,
) -> None:
  if not user_id:
    raise SystemAdminServiceError('userId不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_user_base_info(cur, real_name, phone, email, deps.now_str_func(), user_id)
  conn.commit()
  conn.close()


def delete_user_record(deps: UserRouterDeps, *, user_id: str) -> None:
  if user_id == '1':
    raise SystemAdminServiceError('默认管理员不可删除', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_user(cur, user_id)
  conn.commit()
  conn.close()


def reset_user_password_record(deps: UserRouterDeps, *, user_id: str | None) -> None:
  if not user_id:
    raise SystemAdminServiceError('用户ID不能为空', 400)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_user_password(cur, deps.hash_password_func('123456'), deps.now_str_func(), user_id)
  conn.commit()
  conn.close()


def update_user_enabled_record(deps: UserRouterDeps, *, user_id: str, enabled: int) -> None:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_user_enabled(cur, enabled, deps.now_str_func(), user_id)
  conn.commit()
  conn.close()
