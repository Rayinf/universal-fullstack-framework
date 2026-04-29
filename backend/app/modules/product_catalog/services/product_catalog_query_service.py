from __future__ import annotations

from typing import Any

from app.modules.product_catalog.deps import ProductCatalogRouterDeps
from app.modules.product_catalog.helpers import build_keyword_filter
from app.modules.product_catalog.repositories.product_catalog_repo import (
  query_enabled_product_catalog_rows,
  query_product_catalog_page_rows,
  query_product_catalog_page_total,
)
from app.modules.product_catalog.serializers import build_page_result, product_catalog_to_dict


def query_product_catalog_page(
  deps: ProductCatalogRouterDeps,
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

  keyword_sql, keyword_args = build_keyword_filter(keyword)
  where_sql += keyword_sql
  args.extend(keyword_args)
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    args.append(status)

  total = deps.safe_int_func(query_product_catalog_page_total(cur, where_sql, tuple(args))['cnt'], 0)
  rows = query_product_catalog_page_rows(cur, where_sql, tuple(args), size, (current - 1) * size)
  conn.close()
  return build_page_result(
    [product_catalog_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows],
    total,
    current,
    size,
  )


def list_enabled_product_catalog(deps: ProductCatalogRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_enabled_product_catalog_rows(cur)
  conn.close()
  return [product_catalog_to_dict(row, deps.safe_float_func, deps.safe_int_func) for row in rows]
