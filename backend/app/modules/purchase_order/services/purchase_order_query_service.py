from __future__ import annotations

from typing import Any

from app.modules.purchase_order.deps import PurchaseOrderRouterDeps
from app.modules.purchase_order.helpers import build_purchase_approval_status
from app.modules.purchase_order.repositories.purchase_order_repo import (
  fetch_purchase_order_approval_status_row,
  query_purchase_order_page_rows,
  query_purchase_order_page_total,
)
from app.modules.purchase_order.serializers import build_page_result, purchase_order_to_dict
from app.modules.purchase_order.services.errors import PurchaseOrderServiceError


def query_purchase_order_page(
  deps: PurchaseOrderRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
  status: int | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if keyword and keyword.strip():
    keyword_text = keyword.strip()
    where_sql += ' AND (order_no LIKE ? OR supplier_name LIKE ? OR item_name LIKE ?)'
    values.extend([f'%{keyword_text}%', f'%{keyword_text}%', f'%{keyword_text}%'])
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    values.append(status)

  total = deps.safe_int_func(query_purchase_order_page_total(cur, where_sql, tuple(values))['cnt'], 0)
  rows = query_purchase_order_page_rows(cur, where_sql, tuple(values), size, (current - 1) * size)
  conn.close()
  return build_page_result(
    [purchase_order_to_dict(row, deps.safe_float_func) for row in rows],
    total,
    current,
    size,
  )


def get_purchase_order_approval_status(deps: PurchaseOrderRouterDeps, *, order_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_purchase_order_approval_status_row(cur, order_id)
  if not row:
    conn.close()
    raise PurchaseOrderServiceError('采购单不存在', 404)

  result = build_purchase_approval_status(row, cur, deps.safe_int_func)
  conn.close()
  return result
