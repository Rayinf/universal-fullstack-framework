from __future__ import annotations

from typing import Any

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.repositories.commission_repo import (
  query_commission_export_rows,
  query_commission_page_rows,
  query_commission_page_total,
  query_commission_summary_rows,
)
from app.modules.contracts.serializers import build_page_result, commission_to_dict


def query_commission_page(
  deps: ContractRouterDeps,
  *,
  current: int,
  size: int,
  status: int | None,
  salesperson_name: str | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)
  if salesperson_name and salesperson_name.strip():
    where_sql += ' AND salesperson_name LIKE ?'
    args.append(f'%{salesperson_name.strip()}%')

  total = deps.safe_int_func(query_commission_page_total(cur, where_sql, tuple(args))['cnt'], 0)
  rows = query_commission_page_rows(cur, where_sql, tuple(args), size, (current - 1) * size)
  conn.close()
  return build_page_result(
    [commission_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows],
    total,
    current,
    size,
  )


def export_commission_rows(
  deps: ContractRouterDeps,
  *,
  status: int | None,
  salesperson_name: str | None,
) -> tuple[list[str], list[list[Any]], str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)
  if salesperson_name and salesperson_name.strip():
    where_sql += ' AND salesperson_name LIKE ?'
    args.append(f'%{salesperson_name.strip()}%')

  rows = query_commission_export_rows(cur, where_sql, tuple(args))
  conn.close()
  data_rows = [
    [
      row['contract_no'] or '',
      row['customer_name'] or '',
      row['salesperson_name'] or '',
      deps.safe_float_func(row['contract_amount']),
      deps.safe_float_func(row['payment_amount']),
      deps.safe_float_func(row['commission_rate']),
      deps.safe_float_func(row['commission_amount']),
      '已发放' if deps.safe_int_func(row['status'], 0) == 1 else '待发放',
      row['pay_date'] or '',
      row['create_time'] or '',
    ]
    for row in rows
  ]
  headers = ['合同编号', '客户名称', '销售员', '合同金额', '回款金额', '佣金比例(%)', '佣金金额', '状态', '发放日期', '创建时间']
  return headers, data_rows, '佣金列表'


def get_commission_summary(deps: ContractRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_commission_summary_rows(cur)
  conn.close()
  return [
    {
      'salespersonName': row['salesperson_name'] or '',
      'recordCount': deps.safe_int_func(row['record_count'], 0),
      'totalCommission': deps.safe_float_func(row['total_commission'], 0),
      'paidCommission': deps.safe_float_func(row['paid_commission'], 0),
      'pendingCommission': deps.safe_float_func(row['pending_commission'], 0),
    }
    for row in rows
  ]
