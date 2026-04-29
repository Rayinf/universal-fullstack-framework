from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.helpers import (
  generate_work_order_no,
)
from app.modules.work_order.services.errors import WorkOrderServiceError
from app.modules.work_order.services.work_order_command_service import (
  approve_work_order as approve_work_order_command,
  cancel_work_order as cancel_work_order_command,
  create_work_order as create_work_order_command,
  delete_work_order as delete_work_order_command,
  reject_work_order as reject_work_order_command,
  submit_work_order as submit_work_order_command,
  update_work_order as update_work_order_command,
)
from app.modules.work_order.services.work_order_query_service import (
  export_work_order_rows,
  get_work_order_approval_status as get_work_order_approval_status_query,
  get_work_order_dashboard,
  get_work_order_detail as get_work_order_detail_query,
  list_work_orders as list_work_orders_query,
  query_work_order_page,
)


def register_work_order_routes(router: APIRouter, deps: WorkOrderRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func
  safe_float_func = deps.safe_float_func
  get_current_user_func = deps.get_current_user_func
  export_to_excel_func = deps.export_to_excel_func

  @router.get('/local/work-orders/page')
  def page_work_orders(current: int = 1, size: int = 10, keyword: str | None = None, status: int | None = None) -> dict[str, Any]:
    return ok_func(query_work_order_page(deps, current=current, size=size, keyword=keyword, status=status), 'success')

  @router.get('/local/work-orders/export')
  def export_work_orders(keyword: str | None = None, status: int | None = None) -> Any:
    headers, data_rows, sheet_name = export_work_order_rows(deps, keyword=keyword, status=status)
    return export_to_excel_func(headers, data_rows, sheet_name)

  @router.get('/local/work-orders/dashboard')
  def work_order_dashboard(days: int = 7) -> dict[str, Any]:
    return ok_func(get_work_order_dashboard(deps, days=days), 'success')

  @router.get('/local/work-orders/list')
  def list_work_orders(status: int | None = None) -> dict[str, Any]:
    return ok_func(list_work_orders_query(deps, status=status), 'success')

  @router.get('/local/work-orders/{work_order_id}')
  def get_work_order_detail(work_order_id: str) -> Any:
    try:
      return ok_func(get_work_order_detail_query(deps, work_order_id=work_order_id), 'success')
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/local/work-orders')
  async def create_work_order(request: Request) -> Any:
    payload = await request.json()
    work_order_no = str(payload.get('workOrderNo', '')).strip() or generate_work_order_no()
    contract_id = str(payload.get('contractId', '')).strip()
    contract_no = str(payload.get('contractNo', '')).strip()
    customer_name = str(payload.get('customerName', '')).strip()
    product_id = str(payload.get('productId', '')).strip()
    product_code = str(payload.get('productCode', '')).strip()
    product_name = str(payload.get('productName', '')).strip()
    plan_quantity = safe_float_func(payload.get('planQuantity'), 0)
    work_order_status = safe_int_func(payload.get('status'), 0)
    priority = safe_int_func(payload.get('priority'), 2)
    planned_start_date = str(payload.get('plannedStartDate', '')).strip()
    planned_end_date = str(payload.get('plannedEndDate', '')).strip()
    remark = str(payload.get('remark', '')).strip()
    current_user = get_current_user_func(request)
    applicant = str(payload.get('applicant', '')).strip() or (
      str(current_user['real_name'] or current_user['username']) if current_user else '系统管理员'
    )

    try:
      create_work_order_command(
        deps,
        work_order_no=work_order_no,
        contract_id=contract_id,
        contract_no=contract_no,
        customer_name=customer_name,
        product_id=product_id,
        product_code=product_code,
        product_name=product_name,
        plan_quantity=plan_quantity,
        work_order_status=work_order_status,
        priority=priority,
        planned_start_date=planned_start_date,
        planned_end_date=planned_end_date,
        applicant=applicant,
        remark=remark,
      )
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/local/work-orders/{work_order_id}')
  async def update_work_order(work_order_id: str, request: Request) -> Any:
    payload = await request.json()
    work_order_no = str(payload.get('workOrderNo', '')).strip()
    contract_id = str(payload.get('contractId', '')).strip()
    contract_no = str(payload.get('contractNo', '')).strip()
    customer_name = str(payload.get('customerName', '')).strip()
    product_id = str(payload.get('productId', '')).strip()
    product_code = str(payload.get('productCode', '')).strip()
    product_name = str(payload.get('productName', '')).strip()
    plan_quantity = safe_float_func(payload.get('planQuantity'), 0)
    priority = safe_int_func(payload.get('priority'), 2)
    planned_start_date = str(payload.get('plannedStartDate', '')).strip()
    planned_end_date = str(payload.get('plannedEndDate', '')).strip()
    remark = str(payload.get('remark', '')).strip()

    try:
      update_work_order_command(
        deps,
        work_order_id=work_order_id,
        work_order_no=work_order_no,
        contract_id=contract_id,
        contract_no=contract_no,
        customer_name=customer_name,
        product_id=product_id,
        product_code=product_code,
        product_name=product_name,
        plan_quantity=plan_quantity,
        priority=priority,
        planned_start_date=planned_start_date,
        planned_end_date=planned_end_date,
        remark=remark,
      )
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/work-orders/{work_order_id}')
  def delete_work_order(work_order_id: str) -> Any:
    try:
      delete_work_order_command(deps, work_order_id=work_order_id)
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/work-orders/{work_order_id}/submit')
  def submit_work_order(work_order_id: str) -> Any:
    try:
      submit_work_order_command(deps, work_order_id=work_order_id)
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/work-orders/{work_order_id}/approve')
  def approve_work_order(work_order_id: str, request: Request) -> Any:
    current_user = get_current_user_func(request)
    if not current_user:
      return fail_func('未登录或登录已过期', 401)
    user_id = str(current_user['user_id'])
    user_name = str(current_user['real_name'] or current_user['username'] or user_id)
    try:
      approve_work_order_command(deps, work_order_id=work_order_id, user_id=user_id, user_name=user_name)
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/work-orders/{work_order_id}/reject')
  def reject_work_order(work_order_id: str, request: Request, remark: str | None = None) -> Any:
    current_user = get_current_user_func(request)
    if not current_user:
      return fail_func('未登录或登录已过期', 401)
    user_id = str(current_user['user_id'])
    user_name = str(current_user['real_name'] or current_user['username'] or user_id)
    try:
      reject_work_order_command(
        deps,
        work_order_id=work_order_id,
        user_id=user_id,
        user_name=user_name,
        remark=str(remark or '').strip(),
      )
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/work-orders/{work_order_id}/cancel')
  def cancel_work_order(work_order_id: str) -> Any:
    try:
      cancel_work_order_command(deps, work_order_id=work_order_id)
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/local/work-orders/{work_order_id}/approval-status')
  def get_work_order_approval_status(work_order_id: str) -> Any:
    try:
      return ok_func(get_work_order_approval_status_query(deps, work_order_id=work_order_id), 'success')
    except WorkOrderServiceError as error:
      return fail_func(error.message, error.code)
