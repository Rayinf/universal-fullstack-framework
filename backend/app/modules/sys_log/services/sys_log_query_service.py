from __future__ import annotations

from app.modules.sys_log.deps import SysLogRouterDeps
from app.modules.sys_log.helpers import build_sys_log_filters, normalize_page_params
from app.modules.sys_log.repositories.sys_log_repo import (
  fetch_sys_log_detail,
  query_sys_log_export_rows,
  query_sys_log_page_rows,
  query_sys_log_page_total,
)
from app.modules.sys_log.serializers import build_page_result, build_sys_log_export_csv, sys_log_to_dict
from app.modules.sys_log.services.errors import SysLogServiceError


def query_sys_log_page(
  deps: SysLogRouterDeps,
  *,
  current: int,
  size: int,
  log_type: int | None,
  content: str | None,
  real_name: str | None,
  username: str | None,
  start_time: str | None,
  end_time: str | None,
) -> dict[str, object]:
  page_current, page_size = normalize_page_params(current, size)
  where_sql, values = build_sys_log_filters(
    log_type=log_type,
    content=content,
    real_name=real_name,
    username=username,
    start_time=start_time,
    end_time=end_time,
  )

  conn = deps.get_conn_func()
  cur = conn.cursor()
  total = int(query_sys_log_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_sys_log_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  conn.close()
  return build_page_result([sys_log_to_dict(row) for row in rows], total, page_current, page_size)


def export_sys_logs(deps: SysLogRouterDeps) -> bytes:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_sys_log_export_rows(cur)
  conn.close()
  return build_sys_log_export_csv(rows).encode('utf-8')


def get_sys_log_detail(deps: SysLogRouterDeps, *, log_id: int) -> dict[str, object]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_sys_log_detail(cur, int(log_id))
  conn.close()
  if not row:
    raise SysLogServiceError('日志不存在', 404)
  return sys_log_to_dict(row)
