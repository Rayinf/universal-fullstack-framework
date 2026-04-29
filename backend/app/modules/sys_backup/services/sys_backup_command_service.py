from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any

from app.modules.sys_backup.deps import SysBackupRouterDeps
from app.modules.sys_backup.helpers import parse_sys_backup_config_payload
from app.modules.sys_backup.repositories.sys_backup_repo import (
  delete_sys_backup_config,
  delete_sys_backup_info,
  fetch_sys_backup_config_id,
  insert_sys_backup_config,
  insert_sys_backup_info,
  update_sys_backup_config,
)
from app.modules.sys_backup.services.errors import SysBackupServiceError


def trigger_sys_backup(deps: SysBackupRouterDeps, *, verification_code: str | None) -> bool:
  if not verification_code or not verification_code.strip():
    raise SysBackupServiceError('验证码不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  insert_sys_backup_info(
    cur,
    backup_id=str(uuid.uuid4()),
    file_name=f"local-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}.sql",
    file_content='-- generated local backup',
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def delete_sys_backup(
  deps: SysBackupRouterDeps,
  *,
  backup_id: str,
  verification_code: str | None,
) -> bool:
  if verification_code is not None and not str(verification_code).strip():
    raise SysBackupServiceError('验证码不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_sys_backup_info(cur, backup_id)
  delete_sys_backup_config(cur, backup_id)
  conn.commit()
  conn.close()
  return True


def recovery_sys_backup(*, backup_id: str | None) -> bool:
  return True if backup_id else True


def save_sys_backup_config(deps: SysBackupRouterDeps, *, payload: dict[str, Any]) -> bool:
  parsed = parse_sys_backup_config_payload(deps, payload)
  now = deps.now_str_func()

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if fetch_sys_backup_config_id(cur, parsed['plan_id']):
    update_sys_backup_config(
      cur,
      plan_id=parsed['plan_id'],
      name=parsed['name'],
      enabled=parsed['enabled'],
      cron_expression=parsed['cron_expression'],
      retention_days=parsed['retention_days'],
      now=now,
    )
  else:
    insert_sys_backup_config(
      cur,
      plan_id=parsed['plan_id'],
      name=parsed['name'],
      enabled=parsed['enabled'],
      cron_expression=parsed['cron_expression'],
      retention_days=parsed['retention_days'],
      now=now,
    )
  conn.commit()
  conn.close()
  return True
