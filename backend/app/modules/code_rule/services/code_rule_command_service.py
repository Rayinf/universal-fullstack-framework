from __future__ import annotations

import uuid

from app.modules.code_rule.deps import CodeRuleRouterDeps
from app.modules.code_rule.repositories.code_rule_repo import (
  fetch_code_rule_by_id,
  fetch_code_rule_by_type,
  insert_code_rule,
  update_code_rule as update_code_rule_row,
  update_code_rule_enabled as update_code_rule_enabled_row,
)
from app.modules.code_rule.services.errors import CodeRuleServiceError


def create_code_rule(
  deps: CodeRuleRouterDeps,
  *,
  rule_type: int,
  prefix: str,
  rule_name: str,
  is_enable: int,
  remark: str,
) -> bool:
  if rule_type <= 0 or not prefix or not rule_name:
    raise CodeRuleServiceError('参数不完整', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if fetch_code_rule_by_type(cur, rule_type):
    conn.close()
    raise CodeRuleServiceError('该业务类型已配置规则', 400)

  insert_code_rule(
    cur,
    rule_id=str(uuid.uuid4()),
    rule_type=rule_type,
    prefix=prefix,
    rule_name=rule_name,
    is_enable=is_enable,
    remark=remark,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def update_code_rule(
  deps: CodeRuleRouterDeps,
  *,
  rule_id: str,
  rule_type: int,
  prefix: str,
  rule_name: str,
  is_enable: int,
  remark: str,
) -> bool:
  if not rule_id or rule_type <= 0 or not prefix or not rule_name:
    raise CodeRuleServiceError('参数不完整', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_code_rule_by_id(cur, rule_id):
    conn.close()
    raise CodeRuleServiceError('规则不存在', 404)

  update_code_rule_row(
    cur,
    rule_id=rule_id,
    rule_type=rule_type,
    prefix=prefix,
    rule_name=rule_name,
    is_enable=is_enable,
    remark=remark,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def update_code_rule_enabled(
  deps: CodeRuleRouterDeps,
  *,
  rule_id: str,
  is_enable: int,
) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  update_code_rule_enabled_row(cur, rule_id, deps.safe_int_func(is_enable, 0), deps.now_str_func())
  conn.commit()
  conn.close()
  return True
