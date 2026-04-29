from __future__ import annotations

from typing import Any

from app.modules.customer.deps import CustomerRouterDeps
from app.modules.customer.helpers import build_customer_page_filters
from app.modules.customer.repositories.customer_repo import (
  fetch_customer_by_id,
  query_customer_list_rows,
  query_customer_page_rows,
  query_customer_page_total,
)
from app.modules.customer.serializers import build_page_result, customer_to_dict
from app.modules.customer.services.errors import CustomerServiceError


def query_customer_page(
  deps: CustomerRouterDeps,
  *,
  current: int,
  size: int,
  customer_code: str | None,
  search_key: str | None,
  customer_level: int | None,
  start_date: str | None,
  end_date: str | None,
) -> dict[str, Any]:
  page_current = max(current, 1)
  page_size = max(size, 1)
  where_sql, values = build_customer_page_filters(customer_code, search_key, customer_level, start_date, end_date)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  total = int(query_customer_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_customer_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  conn.close()
  return build_page_result([customer_to_dict(row) for row in rows], total, page_current, page_size)


def query_customer_list(deps: CustomerRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_customer_list_rows(cur)
  conn.close()
  return [customer_to_dict(row) for row in rows]


def get_customer_by_id(deps: CustomerRouterDeps, *, customer_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_customer_by_id(cur, customer_id)
  conn.close()
  if not row:
    raise CustomerServiceError('客户不存在', 404)
  return customer_to_dict(row)
