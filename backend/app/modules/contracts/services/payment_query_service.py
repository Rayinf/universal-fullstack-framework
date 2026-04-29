from __future__ import annotations

from typing import Any

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.repositories.payment_repo import (
  query_payment_export_rows,
  query_payment_page_rows,
  query_payment_page_total,
)
from app.modules.contracts.serializers import build_page_result, payment_to_dict


def query_payment_page(
  deps: ContractRouterDeps,
  *,
  current: int,
  size: int,
  contract_id: str | None,
  status: int | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if contract_id and contract_id.strip():
    where_sql += ' AND p.contract_id = ?'
    args.append(contract_id.strip())
  if status is not None and status >= 0:
    where_sql += ' AND p.status = ?'
    args.append(status)

  total = deps.safe_int_func(query_payment_page_total(cur, where_sql, tuple(args))['cnt'], 0)
  rows = query_payment_page_rows(cur, where_sql, tuple(args), size, (current - 1) * size)
  conn.close()
  return build_page_result(
    [payment_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows],
    total,
    current,
    size,
  )


def export_payment_rows(
  deps: ContractRouterDeps,
  *,
  contract_id: str | None,
  status: int | None,
) -> tuple[list[str], list[list[Any]], str]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  args: list[Any] = []
  if contract_id and contract_id.strip():
    where_sql += ' AND p.contract_id = ?'
    args.append(contract_id.strip())
  if status is not None and status >= 0:
    where_sql += ' AND p.status = ?'
    args.append(status)

  rows = query_payment_export_rows(cur, where_sql, tuple(args))
  conn.close()
  method_map = {1: '转账', 2: '支票', 3: '现金', 4: '承兑'}
  data_rows = [
    [
      row['payment_no'] or '',
      row['contract_no'] or '',
      row['customer_name'] or '',
      deps.safe_float_func(row['payment_amount']),
      row['payment_date'] or '',
      method_map.get(deps.safe_int_func(row['payment_method'], 1), '转账'),
      '已确认' if deps.safe_int_func(row['status'], 0) == 1 else '待确认',
      row['received_by'] or '',
      row['create_time'] or '',
    ]
    for row in rows
  ]
  headers = ['回款单号', '合同编号', '客户名称', '回款金额', '回款日期', '回款方式', '状态', '收款人', '创建时间']
  return headers, data_rows, '回款列表'
