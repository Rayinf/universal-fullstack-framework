from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.helpers import generate_work_inbound_no
from app.modules.work_order.services.errors import WorkOrderServiceError
from app.modules.work_order.services.work_inbound_query_service import export_work_inbound_rows, query_work_inbound_page
from app.modules.work_order.services.work_inbound_service import create_work_inbound as create_work_inbound_command


def register_work_inbound_routes(router: APIRouter, deps: WorkOrderRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  now_str_func = deps.now_str_func
  safe_float_func = deps.safe_float_func
  get_current_user_func = deps.get_current_user_func
  export_to_excel_func = deps.export_to_excel_func

  @router.get('/local/work-inbounds/page')
  def page_work_inbounds(current: int = 1, size: int = 10, keyword: str | None = None, workOrderId: str | None = None) -> dict[str, Any]:
    return ok_func(
      query_work_inbound_page(deps, current=current, size=size, keyword=keyword, work_order_id=workOrderId),
      'success',
    )

  @router.get('/local/work-inbounds/export')
  def export_work_inbounds(keyword: str | None = None, workOrderId: str | None = None) -> Any:
    headers, data_rows, sheet_name = export_work_inbound_rows(deps, keyword=keyword, work_order_id=workOrderId)
    return export_to_excel_func(headers, data_rows, sheet_name)

  @router.post('/local/work-inbounds')
  async def create_work_inbound(request: Request) -> Any:
    payload = await request.json()
    work_order_id = str(payload.get('workOrderId', '')).strip()
    inbound_no = str(payload.get('inboundNo', '')).strip() or generate_work_inbound_no()
    quantity = safe_float_func(payload.get('quantity'), 0)
    warehouse_name = str(payload.get('warehouseName', '')).strip() or '成品仓'
    inbound_time = str(payload.get('inboundTime', '')).strip() or now_str_func()
    remark = str(payload.get('remark', '')).strip()
    current_user = get_current_user_func(request)
    operator_name = str(current_user['real_name'] or current_user['username']) if current_user else '系统管理员'

    try:
      create_work_inbound_command(
        deps,
        work_order_id=work_order_id,
        inbound_no=inbound_no,
        quantity=quantity,
        warehouse_name=warehouse_name,
        operator_name=operator_name,
        inbound_time=inbound_time,
        remark=remark,
      )
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
