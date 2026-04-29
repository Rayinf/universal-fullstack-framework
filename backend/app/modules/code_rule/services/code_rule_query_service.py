from __future__ import annotations

from app.modules.code_rule.deps import CodeRuleRouterDeps
from app.modules.code_rule.helpers import build_code_rule_filters, generate_code_value, normalize_pagination
from app.modules.code_rule.repositories.code_rule_repo import (
  fetch_code_rule_detail,
  fetch_code_rule_prefix_by_type,
  query_code_rule_page_rows,
  query_code_rule_page_total,
)
from app.modules.code_rule.serializers import build_page_result, code_rule_to_dict
from app.modules.code_rule.services.errors import CodeRuleServiceError


def query_code_rule_page(
  deps: CodeRuleRouterDeps,
  *,
  page: int | None,
  current: int | None,
  size: int,
  rule_type: int | None,
  keyword: str | None,
) -> dict[str, object]:
  page_current, page_size = normalize_pagination(page, current, size)
  where_sql, values = build_code_rule_filters(rule_type, keyword)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  total = int(query_code_rule_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_code_rule_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  conn.close()
  return build_page_result([code_rule_to_dict(row) for row in rows], total, page_current, page_size)


def get_code_rule_detail_by_id(deps: CodeRuleRouterDeps, *, rule_id: str) -> dict[str, object]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_code_rule_detail(cur, rule_id)
  conn.close()
  if not row:
    raise CodeRuleServiceError('规则不存在', 404)
  return code_rule_to_dict(row)


def get_code_by_rule_type(deps: CodeRuleRouterDeps, *, code_type: int) -> str:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_code_rule_prefix_by_type(cur, deps.safe_int_func(code_type, 0))
  conn.close()
  prefix = row['prefix'] if row else 'CODE'
  return generate_code_value(prefix)
