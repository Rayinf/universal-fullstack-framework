from __future__ import annotations

from typing import Any

from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.repositories.work_inbound_repo import (
  query_work_inbound_export_rows,
  query_work_inbound_page_rows,
  query_work_inbound_page_total,
)
from app.modules.work_order.serializers import build_page_result, work_inbound_to_dict


def query_work_inbound_page(
  deps: WorkOrderRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
  work_order_id: str | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if keyword and keyword.strip():
    kw = keyword.strip()
    where_sql += ' AND (wi.inbound_no LIKE ? OR wi.work_order_no LIKE ? OR wo.product_name LIKE ? OR wo.customer_name LIKE ?)'
    args.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%', f'%{kw}%'])
  if work_order_id and work_order_id.strip():
    where_sql += ' AND wi.work_order_id = ?'
    args.append(work_order_id.strip())

  total = deps.safe_int_func(query_work_inbound_page_total(cur, where_sql, tuple(args))['cnt'], 0)
  offset = (current - 1) * size
  rows = query_work_inbound_page_rows(cur, where_sql, tuple(args), size, offset)
  conn.close()
  return build_page_result([work_inbound_to_dict(row, deps.safe_float_func) for row in rows], total, current, size)


def export_work_inbound_rows(
  deps: WorkOrderRouterDeps,
  *,
  keyword: str | None,
  work_order_id: str | None,
) -> tuple[list[str], list[list[Any]], str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if keyword and keyword.strip():
    kw = keyword.strip()
    where_sql += ' AND (wi.inbound_no LIKE ? OR wi.work_order_no LIKE ? OR wo.product_name LIKE ? OR wo.customer_name LIKE ?)'
    args.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%', f'%{kw}%'])
  if work_order_id and work_order_id.strip():
    where_sql += ' AND wi.work_order_id = ?'
    args.append(work_order_id.strip())

  rows = query_work_inbound_export_rows(cur, where_sql, tuple(args))
  conn.close()
  data_rows = [
    [
      row['inbound_no'] or '',
      row['work_order_no'] or '',
      row['product_name'] or '',
      row['customer_name'] or '',
      deps.safe_float_func(row['quantity']),
      row['warehouse_name'] or '',
      row['operator_name'] or '',
      row['inbound_time'] or '',
      row['remark'] or '',
    ]
    for row in rows
  ]
  headers = ['入库单号', '工单号', '产品', '客户', '入库数量', '仓库', '操作人', '入库时间', '备注']
  return headers, data_rows, '完工入库记录'
