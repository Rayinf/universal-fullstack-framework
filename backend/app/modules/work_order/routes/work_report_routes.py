from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.services.errors import WorkOrderServiceError
from app.modules.work_order.services.work_report_query_service import export_work_report_rows, query_work_report_page
from app.modules.work_order.services.work_report_service import create_work_report as create_work_report_command


def register_work_report_routes(router: APIRouter, deps: WorkOrderRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  now_str_func = deps.now_str_func
  safe_float_func = deps.safe_float_func
  get_current_user_func = deps.get_current_user_func
  export_to_excel_func = deps.export_to_excel_func

  @router.get('/local/work-reports/page')
  def page_work_reports(current: int = 1, size: int = 10, keyword: str | None = None, workOrderId: str | None = None) -> dict[str, Any]:
    return ok_func(
      query_work_report_page(deps, current=current, size=size, keyword=keyword, work_order_id=workOrderId),
      'success',
    )

  @router.get('/local/work-reports/export')
  def export_work_reports(keyword: str | None = None, workOrderId: str | None = None) -> Any:
    headers, data_rows, sheet_name = export_work_report_rows(deps, keyword=keyword, work_order_id=workOrderId)
    return export_to_excel_func(headers, data_rows, sheet_name)

  @router.post('/local/work-reports')
  async def create_work_report(request: Request) -> Any:
    payload = await request.json()
    work_order_id = str(payload.get('workOrderId', '')).strip()
    process_name = str(payload.get('processName', '')).strip()
    report_quantity = safe_float_func(payload.get('reportQuantity'), 0)
    qualified_quantity = safe_float_func(payload.get('qualifiedQuantity'), 0)
    defect_quantity = safe_float_func(payload.get('defectQuantity'), 0)
    report_time = str(payload.get('reportTime', '')).strip() or now_str_func()
    remark = str(payload.get('remark', '')).strip()
    current_user = get_current_user_func(request)
    report_user_id = str(current_user['user_id']) if current_user else '0'
    report_user_name = str(current_user['real_name'] or current_user['username'] or report_user_id) if current_user else '系统管理员'

    try:
      create_work_report_command(
        deps,
        work_order_id=work_order_id,
        process_name=process_name,
        report_quantity=report_quantity,
        qualified_quantity=qualified_quantity,
        defect_quantity=defect_quantity,
        report_user_id=report_user_id,
        report_user_name=report_user_name,
        report_time=report_time,
        remark=remark,
      )
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
