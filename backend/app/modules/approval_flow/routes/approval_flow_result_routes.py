from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.approval_flow.deps import ApprovalFlowRouterDeps
from app.modules.approval_flow.services.approval_flow_result_command_service import (
  save_approval_result as save_approval_result_command,
)
from app.modules.approval_flow.services.approval_flow_result_query_service import (
  get_approval_result_list as get_approval_result_list_query,
  get_order_scheduling_result as get_order_scheduling_result_query,
  get_order_scheduling_result_for_all as get_order_scheduling_result_for_all_query,
  query_approval_flow_result_page,
)
from app.modules.approval_flow.services.errors import ApprovalFlowServiceError


def register_approval_flow_result_routes(router: APIRouter, deps: ApprovalFlowRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func

  @router.get('/manage/api/approvalFlowResult/page')
  def page_approval_flow_result(
    current: int = 1,
    size: int = 10,
    keyword: str | None = None,
    processPeopleId: str | None = None,
    approvalStatus: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_approval_flow_result_page(
        deps,
        current=current,
        size=size,
        keyword=keyword,
        process_people_id=processPeopleId,
        approval_status=approvalStatus,
      ),
      'success',
    )

  @router.post('/manage/api/approvalFlowResult/getApprovalResultList')
  async def get_approval_result_list(request: Request) -> dict[str, Any]:
    payload = await request.json()
    return ok_func(
      get_approval_result_list_query(
        deps,
        process_people_id=str(payload.get('processPeopleId', '')).strip(),
        approval_status=safe_int_func(payload.get('approvalStatus'), 3),
      ),
      'success',
    )

  @router.post('/manage/api/approvalFlowResult/saveApprovalResult')
  async def save_approval_result(request: Request) -> Any:
    payload = await request.json()
    order_scheduling_id = str(payload.get('orderSchedulingId', '')).strip()
    try:
      save_approval_result_command(
        deps,
        record_id=safe_int_func(payload.get('id'), 0),
        order_id=str(payload.get('orderId', '')).strip(),
        order_scheduling_id=order_scheduling_id,
        order_name=str(payload.get('orderName', '')).strip() or f'排程-{order_scheduling_id}',
        product_name=str(payload.get('productName', '')).strip() or '',
        process_library_id=str(payload.get('processLibraryId', '')).strip(),
        approval_flow_id=safe_int_func(payload.get('approvalFlowId'), 0),
        process_people=str(payload.get('processPeople', '')).strip() or '1',
        approval_status=safe_int_func(payload.get('approvalStatus'), 3),
        approval_remarks=str(payload.get('approvalRemarks', '')).strip(),
      )
    except ApprovalFlowServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/manage/api/approvalFlowResult/getOrderSchedulingResult')
  def get_order_scheduling_result(orderSchedulingId: str, processPeopleId: str | None = None) -> dict[str, Any]:
    return ok_func(
      get_order_scheduling_result_query(
        deps,
        order_scheduling_id=orderSchedulingId,
        process_people_id=processPeopleId,
      ),
      'success',
    )

  @router.get('/manage/api/approvalFlowResult/getOrderSchedulingResultForAll')
  def get_order_scheduling_result_for_all(orderSchedulingId: str) -> dict[str, Any]:
    return ok_func(get_order_scheduling_result_for_all_query(deps, order_scheduling_id=orderSchedulingId), 'success')
