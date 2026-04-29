from __future__ import annotations

from typing import Any

from app.modules.quotation.deps import QuotationRouterDeps
from app.modules.quotation.helpers import build_quotation_approval_status, quotation_items_to_list
from app.modules.quotation.repositories.quotation_repo import (
  fetch_quotation_approval_status_row,
  fetch_quotation_detail_row,
  query_quotation_page_rows,
  query_quotation_page_total,
)
from app.modules.quotation.serializers import build_page_result, quotation_to_dict
from app.modules.quotation.services.errors import QuotationServiceError


def query_quotation_page(
  deps: QuotationRouterDeps,
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
    where_sql += ' AND (quote_no LIKE ? OR customer_name LIKE ? OR contact_person LIKE ?)'
    args.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%'])
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)

  total = deps.safe_int_func(query_quotation_page_total(cur, where_sql, tuple(args))['cnt'], 0)
  offset = (current - 1) * size
  rows = query_quotation_page_rows(cur, where_sql, tuple(args), size, offset)
  conn.close()
  return build_page_result(
    [quotation_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows],
    total,
    current,
    size,
  )


def get_quotation_detail(deps: QuotationRouterDeps, *, quotation_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_quotation_detail_row(cur, quotation_id)
  if not row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  result = quotation_to_dict(row, deps.safe_float_func, deps.safe_int_func)
  result['items'] = quotation_items_to_list(cur, quotation_id, deps.safe_float_func, deps.safe_int_func)
  conn.close()
  return result


def get_quotation_approval_status(deps: QuotationRouterDeps, *, quotation_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_quotation_approval_status_row(cur, quotation_id)
  if not row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  result = build_quotation_approval_status(row, cur, deps.safe_int_func)
  conn.close()
  return result
