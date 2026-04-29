from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.repositories.commission_repo import query_dashboard_commission_rows
from app.modules.contracts.repositories.contract_repo import (
  fetch_contract_detail_row,
  query_contract_export_rows,
  query_contract_page_rows,
  query_contract_page_total,
  query_contract_payment_summary_rows,
  query_dashboard_contract_rows,
  query_dashboard_customer_amount_rows,
  query_dashboard_quotation_rows,
)
from app.modules.contracts.repositories.payment_repo import query_dashboard_payment_rows
from app.modules.contracts.serializers import build_page_result, contract_to_dict
from app.modules.contracts.services.errors import ContractServiceError


def query_contract_page(
  deps: ContractRouterDeps,
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
    where_sql += ' AND (contract_no LIKE ? OR customer_name LIKE ? OR contract_name LIKE ?)'
    args.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%'])
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)

  total = deps.safe_int_func(query_contract_page_total(cur, where_sql, tuple(args))['cnt'], 0)
  rows = query_contract_page_rows(cur, where_sql, tuple(args), size, (current - 1) * size)
  conn.close()
  return build_page_result(
    [contract_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows],
    total,
    current,
    size,
  )


def export_contract_rows(
  deps: ContractRouterDeps,
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
    where_sql += ' AND (contract_no LIKE ? OR customer_name LIKE ? OR contract_name LIKE ?)'
    args.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%'])
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)

  rows = query_contract_export_rows(cur, where_sql, tuple(args))
  conn.close()
  data_rows = [
    [
      row['contract_no'] or '',
      row['customer_name'] or '',
      row['contract_name'] or '',
      deps.safe_float_func(row['total_amount']),
      deps.safe_float_func(row['paid_amount']),
      row['signed_date'] or '',
      row['start_date'] or '',
      row['end_date'] or '',
      deps.safe_int_func(row['status'], 0),
      row['update_time'] or '',
    ]
    for row in rows
  ]
  headers = ['合同编号', '客户名称', '合同名称', '合同金额', '已回款', '签订日期', '开始日期', '结束日期', '状态', '更新时间']
  return headers, data_rows, '合同列表'


def get_contract_detail(deps: ContractRouterDeps, *, contract_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_contract_detail_row(cur, contract_id)
  conn.close()
  if not row:
    raise ContractServiceError('合同不存在', 404)
  return contract_to_dict(row, deps.safe_float_func, deps.safe_int_func)


def get_contract_payment_summary(deps: ContractRouterDeps, *, contract_id: str | None) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1=1'
  args: list[Any] = []
  if contract_id and contract_id.strip():
    where_sql += ' AND c.id = ?'
    args.append(contract_id.strip())
  rows = query_contract_payment_summary_rows(cur, where_sql, tuple(args))
  conn.close()
  return [
    {
      'contractId': str(row['contract_id']),
      'contractNo': row['contract_no'] or '',
      'customerName': row['customer_name'] or '',
      'totalAmount': deps.safe_float_func(row['total_amount']),
      'paidAmount': deps.safe_float_func(row['paid_amount']),
      'paidRate': deps.safe_float_func(row['paid_rate']),
    }
    for row in rows
  ]


def get_contract_dashboard(deps: ContractRouterDeps) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  quotation_rows = query_dashboard_quotation_rows(cur)
  contract_rows = query_dashboard_contract_rows(cur)
  payment_rows = query_dashboard_payment_rows(cur)
  customer_rows = query_dashboard_customer_amount_rows(cur)
  commission_rows = query_dashboard_commission_rows(cur)

  total_quotes = len(quotation_rows)
  approved_quotes = len([row for row in quotation_rows if deps.safe_int_func(row['status'], 0) in (2, 4)])
  conversion_rate = round((approved_quotes * 100.0 / total_quotes), 2) if total_quotes > 0 else 0
  contract_total_amount = round(sum(deps.safe_float_func(row['total_amount'], 0) for row in contract_rows), 2)
  contract_paid_amount = round(sum(deps.safe_float_func(row['paid_amount'], 0) for row in contract_rows), 2)
  overall_paid_rate = round((contract_paid_amount * 100.0 / contract_total_amount), 2) if contract_total_amount > 0 else 0
  pending_approval = len([row for row in quotation_rows if deps.safe_int_func(row['status'], 0) == 1])

  today = datetime.now().strftime('%Y-%m-%d')
  soon_deadline = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
  expiring_contracts = len(
    [
      row
      for row in contract_rows
      if str(row['end_date'] or '') and today <= str(row['end_date']) <= soon_deadline and deps.safe_int_func(row['status'], 0) in (1, 2)
    ],
  )

  month_keys: list[str] = []
  cursor_date = datetime.now().replace(day=1)
  for _ in range(6):
    month_keys.append(cursor_date.strftime('%Y-%m'))
    if cursor_date.month == 1:
      cursor_date = cursor_date.replace(year=cursor_date.year - 1, month=12)
    else:
      cursor_date = cursor_date.replace(month=cursor_date.month - 1)
  month_keys = list(reversed(month_keys))
  payment_map: dict[str, float] = {key: 0.0 for key in month_keys}
  for row in payment_rows:
    if deps.safe_int_func(row['status'], 0) != 1:
      continue
    month_key = str(row['create_time'] or '')[:7]
    if month_key in payment_map:
      payment_map[month_key] += deps.safe_float_func(row['payment_amount'], 0)

  customer_map: dict[str, float] = {}
  for row in customer_rows:
    customer = str(row['customer_name'] or '未知客户')
    customer_map[customer] = customer_map.get(customer, 0) + deps.safe_float_func(row['total_amount'], 0)
  customer_top = sorted(customer_map.items(), key=lambda item: item[1], reverse=True)[:10]

  salesperson_map: dict[str, float] = {}
  for row in commission_rows:
    salesperson = str(row['salesperson_name'] or '未命名')
    salesperson_map[salesperson] = salesperson_map.get(salesperson, 0) + deps.safe_float_func(row['commission_amount'], 0)
  commission_top = sorted(salesperson_map.items(), key=lambda item: item[1], reverse=True)[:5]

  conn.close()
  return {
    'cards': {
      'pendingApprovalCount': pending_approval,
      'contractTotalAmount': contract_total_amount,
      'overallPaidRate': overall_paid_rate,
      'expiringContractCount': expiring_contracts,
      'quotationConversionRate': conversion_rate,
    },
    'paymentTrend': [{'month': key, 'amount': round(amount, 2)} for key, amount in payment_map.items()],
    'customerContributionTop': [{'customerName': item[0], 'amount': round(item[1], 2)} for item in customer_top],
    'commissionTop': [{'salespersonName': item[0], 'amount': round(item[1], 2)} for item in commission_top],
  }
