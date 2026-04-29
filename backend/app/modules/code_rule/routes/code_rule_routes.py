from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.code_rule.deps import CodeRuleRouterDeps
from app.modules.code_rule.helpers import parse_code_rule_payload
from app.modules.code_rule.services.code_rule_command_service import (
  create_code_rule as create_code_rule_command,
  update_code_rule as update_code_rule_command,
  update_code_rule_enabled as update_code_rule_enabled_command,
)
from app.modules.code_rule.services.code_rule_query_service import (
  get_code_by_rule_type,
  get_code_rule_detail_by_id,
  query_code_rule_page,
)
from app.modules.code_rule.services.errors import CodeRuleServiceError


def register_code_rule_routes(router: APIRouter, deps: CodeRuleRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/manage/api/codeRule/page')
  def page_code_rule(
    page: int | None = None,
    current: int | None = None,
    size: int = 10,
    type: int | None = None,
    keyword: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_code_rule_page(
        deps,
        page=page,
        current=current,
        size=size,
        rule_type=type,
        keyword=keyword,
      ),
      'success',
    )

  @router.get('/manage/api/codeRule/{rule_id}')
  def get_code_rule(rule_id: str) -> Any:
    try:
      return ok_func(get_code_rule_detail_by_id(deps, rule_id=rule_id), 'success')
    except CodeRuleServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/manage/api/codeRule/save')
  async def save_code_rule(request: Request) -> Any:
    payload = parse_code_rule_payload(await request.json(), deps.safe_int_func)
    try:
      create_code_rule_command(
        deps,
        rule_type=payload['type'],
        prefix=payload['prefix'],
        rule_name=payload['rule_name'],
        is_enable=payload['is_enable'],
        remark=payload['remark'],
      )
    except CodeRuleServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/codeRule/update')
  async def update_code_rule(request: Request) -> Any:
    payload = parse_code_rule_payload(await request.json(), deps.safe_int_func)
    try:
      update_code_rule_command(
        deps,
        rule_id=payload['id'],
        rule_type=payload['type'],
        prefix=payload['prefix'],
        rule_name=payload['rule_name'],
        is_enable=payload['is_enable'],
        remark=payload['remark'],
      )
    except CodeRuleServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/codeRule/enableCodeRule')
  def enable_code_rule(id: str, isEnable: int) -> dict[str, Any]:
    update_code_rule_enabled_command(deps, rule_id=id, is_enable=isEnable)
    return ok_func(True, 'success')

  @router.post('/manage/api/codeRule/getCode')
  def get_code_by_rule(codeType: int) -> dict[str, Any]:
    return ok_func(get_code_by_rule_type(deps, code_type=codeType), 'success')
