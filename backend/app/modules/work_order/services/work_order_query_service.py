from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.helpers import build_work_order_approval_status
from app.modules.work_order.repositories.work_inbound_repo import query_inbound_trend_rows
from app.modules.work_order.repositories.work_order_repo import (
  fetch_work_order_approval_status_row,
  fetch_work_order_detail_row,
  query_work_order_export_rows,
  query_work_order_list_rows,
  query_work_order_page_rows,
  query_work_order_page_total,
  query_work_order_product_plan_rows,
  query_work_order_status_rows,
)
from app.modules.work_order.repositories.work_report_repo import query_report_trend_rows
from app.modules.work_order.serializers import build_page_result, work_order_to_dict
from app.modules.work_order.services.errors import WorkOrderServiceError


def query_work_order_page(
  deps: WorkOrderRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
  status: int | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if keyword and keyword.strip():
    kw = keyword.strip()
    where_sql += ' AND (work_order_no LIKE ? OR contract_no LIKE ? OR customer_name LIKE ? OR product_name LIKE ?)'
    args.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%', f'%{kw}%'])
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)

  total = deps.safe_int_func(query_work_order_page_total(cur, where_sql, tuple(args))['cnt'], 0)
  offset = (current - 1) * size
  rows = query_work_order_page_rows(cur, where_sql, tuple(args), size, offset)
  conn.close()
  return build_page_result(
    [work_order_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows],
    total,
    current,
    size,
  )


def export_work_order_rows(
  deps: WorkOrderRouterDeps,
  *,
  keyword: str | None,
  status: int | None,
) -> tuple[list[str], list[list[Any]], str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if keyword and keyword.strip():
    kw = keyword.strip()
    where_sql += ' AND (work_order_no LIKE ? OR contract_no LIKE ? OR customer_name LIKE ? OR product_name LIKE ?)'
    args.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%', f'%{kw}%'])
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)

  rows = query_work_order_export_rows(cur, where_sql, tuple(args))
  conn.close()
  status_map = {0: '草稿', 1: '待审批', 2: '已审批', 3: '生产中', 4: '待入库', 5: '已完结', 6: '已驳回', 7: '已作废'}
  data_rows = [
    [
      row['work_order_no'] or '',
      row['contract_no'] or '',
      row['customer_name'] or '',
      row['product_name'] or '',
      deps.safe_float_func(row['plan_quantity']),
      deps.safe_float_func(row['reported_quantity']),
      deps.safe_float_func(row['qualified_quantity']),
      deps.safe_float_func(row['inbound_quantity']),
      status_map.get(deps.safe_int_func(row['status'], 0), '未知'),
      row['planned_start_date'] or '',
      row['planned_end_date'] or '',
      row['update_time'] or '',
    ]
    for row in rows
  ]
  headers = ['工单号', '合同号', '客户', '产品', '计划数', '报工数', '合格数', '入库数', '状态', '计划开始', '计划结束', '更新时间']
  return headers, data_rows, '生产工单列表'


def get_work_order_dashboard(deps: WorkOrderRouterDeps, *, days: int) -> dict[str, Any]:
  if days not in (7, 30):
    days = 7
  conn = deps.get_conn_func()
  cur = conn.cursor()
  status_rows = query_work_order_status_rows(cur)
  total_count = len(status_rows)
  pending_approval_count = len([row for row in status_rows if deps.safe_int_func(row['status'], 0) == 1])
  producing_count = len([row for row in status_rows if deps.safe_int_func(row['status'], 0) == 3])
  pending_inbound_count = len([row for row in status_rows if deps.safe_int_func(row['status'], 0) == 4])
  completed_count = len([row for row in status_rows if deps.safe_int_func(row['status'], 0) == 5])
  completion_rate = round((completed_count * 100.0 / total_count), 2) if total_count > 0 else 0

  date_keys: list[str] = []
  for idx in range(days - 1, -1, -1):
    date_keys.append((datetime.now() - timedelta(days=idx)).strftime('%Y-%m-%d'))
  report_trend_map: dict[str, float] = {date_key: 0.0 for date_key in date_keys}
  inbound_trend_map: dict[str, float] = {date_key: 0.0 for date_key in date_keys}

  for row in query_report_trend_rows(cur):
    day_key = str(row['report_time'] or '')[:10]
    if day_key in report_trend_map:
      report_trend_map[day_key] += deps.safe_float_func(row['qualified_quantity'], 0)

  for row in query_inbound_trend_rows(cur):
    day_key = str(row['inbound_time'] or '')[:10]
    if day_key in inbound_trend_map:
      inbound_trend_map[day_key] += deps.safe_float_func(row['quantity'], 0)

  status_count_map = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
  for row in status_rows:
    status_value = deps.safe_int_func(row['status'], 0)
    status_count_map[status_value] = status_count_map.get(status_value, 0) + 1
  status_name_map = {0: '草稿', 1: '待审批', 2: '已审批', 3: '生产中', 4: '待入库', 5: '已完结', 6: '已驳回', 7: '已作废'}

  product_qty_map: dict[str, float] = {}
  for row in query_work_order_product_plan_rows(cur):
    product_name = str(row['product_name'] or '未命名产品')
    product_qty_map[product_name] = product_qty_map.get(product_name, 0) + deps.safe_float_func(row['plan_quantity'], 0)
  product_top = sorted(product_qty_map.items(), key=lambda item: item[1], reverse=True)[:10]
  conn.close()
  return {
    'cards': {
      'totalCount': total_count,
      'pendingApprovalCount': pending_approval_count,
      'producingCount': producing_count,
      'pendingInboundCount': pending_inbound_count,
      'completedCount': completed_count,
      'completionRate': completion_rate,
    },
    'reportTrend': [{'date': date_key, 'quantity': round(report_trend_map[date_key], 2)} for date_key in date_keys],
    'inboundTrend': [{'date': date_key, 'quantity': round(inbound_trend_map[date_key], 2)} for date_key in date_keys],
    'statusDistribution': [
      {'status': status_value, 'statusName': status_name_map.get(status_value, str(status_value)), 'count': count}
      for status_value, count in status_count_map.items()
    ],
    'productTop': [{'productName': item[0], 'quantity': round(item[1], 2)} for item in product_top],
  }


def list_work_orders(deps: WorkOrderRouterDeps, *, status: int | None) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)
  rows = query_work_order_list_rows(cur, where_sql, tuple(args))
  conn.close()
  return [work_order_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows]


def get_work_order_detail(deps: WorkOrderRouterDeps, *, work_order_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_work_order_detail_row(cur, work_order_id)
  if not row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  result = work_order_to_dict(row, deps.safe_float_func, deps.safe_int_func)
  conn.close()
  return result


def get_work_order_approval_status(deps: WorkOrderRouterDeps, *, work_order_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_work_order_approval_status_row(cur, work_order_id)
  if not row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  result = build_work_order_approval_status(row, cur, deps.safe_int_func)
  conn.close()
  return result
