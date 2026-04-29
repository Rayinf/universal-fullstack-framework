from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.approval_flow.deps import ApprovalFlowRouterDeps
from app.modules.approval_flow.services.approval_flow_command_service import (
  create_approval_flow as create_approval_flow_command,
  delete_approval_flow as delete_approval_flow_command,
  save_approval_flow_nodes as save_approval_flow_nodes_command,
  update_approval_flow as update_approval_flow_command,
)
from app.modules.approval_flow.services.approval_flow_query_service import (
  get_approval_flow_detail as get_approval_flow_detail_query,
  list_approval_flows as list_approval_flows_query,
  query_approval_flow_page,
)
from app.modules.approval_flow.services.errors import ApprovalFlowServiceError


def register_approval_flow_routes(router: APIRouter, deps: ApprovalFlowRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func

  @router.get('/manage/api/approvalFlow/page')
  def page_approval_flow(
    current: int = 1,
    size: int = 10,
    keyword: str | None = None,
    approvalType: int | None = None,
    status: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_approval_flow_page(
        deps,
        current=current,
        size=size,
        keyword=keyword,
        approval_type=approvalType,
        status=status,
      ),
      'success',
    )

  @router.get('/manage/api/approvalFlow/list')
  def list_approval_flow() -> dict[str, Any]:
    return ok_func(list_approval_flows_query(deps), 'success')

  @router.get('/manage/api/approvalFlow/detailByApprovalFlowId')
  def detail_by_approval_flow_id(approvalFlowId: int) -> Any:
    try:
      return ok_func(get_approval_flow_detail_query(deps, approval_flow_id=int(approvalFlowId)), 'success')
    except ApprovalFlowServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/manage/api/approvalFlow/save')
  async def save_approval_flow(request: Request) -> Any:
    payload = await request.json()
    try:
      create_approval_flow_command(
        deps,
        approval_flow_name=str(payload.get('approvalFlowName', '')).strip(),
        approval_type=safe_int_func(payload.get('approvalType'), 1),
        process_library_id=str(payload.get('processLibraryId', '')).strip(),
        status=safe_int_func(payload.get('status'), 1),
        remarks=str(payload.get('remarks', '')).strip(),
      )
    except ApprovalFlowServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/approvalFlow/update')
  async def update_approval_flow(request: Request) -> Any:
    payload = await request.json()
    try:
      update_approval_flow_command(
        deps,
        flow_id=safe_int_func(payload.get('id'), 0),
        approval_flow_name=str(payload.get('approvalFlowName', '')).strip(),
        approval_type=safe_int_func(payload.get('approvalType'), 1),
        process_library_id=str(payload.get('processLibraryId', '')).strip(),
        status=safe_int_func(payload.get('status'), 1),
        remarks=str(payload.get('remarks', '')).strip(),
      )
    except ApprovalFlowServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/manage/api/approvalFlow/{flow_id}')
  def delete_approval_flow(flow_id: int) -> dict[str, Any]:
    delete_approval_flow_command(deps, flow_id=int(flow_id))
    return ok_func(True, 'success')

  @router.post('/manage/api/approvalFlow/saveApprovalFlowNodeInfo')
  async def save_approval_flow_node_info(request: Request) -> Any:
    payload = await request.json()
    if not isinstance(payload, list):
      return fail_func('节点数据格式错误', 400)
    if not payload:
      return ok_func(True, 'success')
    try:
      save_approval_flow_nodes_command(deps, payload=payload)
    except ApprovalFlowServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
