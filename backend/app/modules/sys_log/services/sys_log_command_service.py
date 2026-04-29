from __future__ import annotations

from app.modules.sys_log.deps import SysLogRouterDeps
from app.modules.sys_log.helpers import build_clear_cutoff
from app.modules.sys_log.repositories.sys_log_repo import (
  clear_sys_logs_by_type,
  clear_sys_logs_by_type_with_cutoff,
  delete_sys_logs_by_ids,
)
from app.modules.sys_log.services.errors import SysLogServiceError


def delete_sys_logs(deps: SysLogRouterDeps, *, id_list: list[str]) -> bool:
  if not id_list:
    raise SysLogServiceError('idList不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_sys_logs_by_ids(cur, id_list)
  conn.commit()
  conn.close()
  return True


def clear_sys_logs(deps: SysLogRouterDeps, *, log_type: int, clear_type: int) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  if int(clear_type) == 9:
    clear_sys_logs_by_type(cur, int(log_type))
  else:
    clear_sys_logs_by_type_with_cutoff(cur, int(log_type), build_clear_cutoff(int(clear_type)))
  conn.commit()
  conn.close()
  return True
