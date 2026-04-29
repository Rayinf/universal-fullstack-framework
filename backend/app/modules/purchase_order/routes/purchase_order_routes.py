from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.purchase_order.deps import PurchaseOrderRouterDeps
from app.modules.purchase_order.helpers import generate_order_no
from app.modules.purchase_order.services.errors import PurchaseOrderServiceError
from app.modules.purchase_order.services.purchase_order_command_service import (
  approve_purchase_order as approve_purchase_order_command,
  cancel_purchase_order as cancel_purchase_order_command,
  create_purchase_order as create_purchase_order_command,
  delete_purchase_order as delete_purchase_order_command,
  submit_purchase_order as submit_purchase_order_command,
  update_purchase_order as update_purchase_order_command,
)
from app.modules.purchase_order.services.purchase_order_query_service import (
  get_purchase_order_approval_status as get_purchase_order_approval_status_query,
  query_purchase_order_page,
)


def register_purchase_order_routes(router: APIRouter, deps: PurchaseOrderRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func
  safe_float_func = deps.safe_float_func
  get_current_user_func = deps.get_current_user_func

  @router.get('/local/purchase-orders/page')
  def page_purchase_orders(
    current: int = 1,
    size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(query_purchase_order_page(deps, current=current, size=size, keyword=keyword, status=status), 'success')

  @router.post('/local/purchase-orders')
  async def create_purchase_order(request: Request) -> Any:
    payload = await request.json()
    order_no = str(payload.get('orderNo', '') or '').strip() or generate_order_no()
    supplier_name = str(payload.get('supplierName', '')).strip()
    item_name = str(payload.get('itemName', '')).strip()
    quantity = safe_float_func(payload.get('quantity'), 0)
    unit_price = safe_float_func(payload.get('unitPrice'), 0)
    total_amount = safe_float_func(payload.get('totalAmount'), 0)
    order_status = safe_int_func(payload.get('status'), 0)
    applicant = str(payload.get('applicant', '')).strip() or '系统管理员'
    remark = str(payload.get('remark', '')).strip()

    try:
      create_purchase_order_command(
        deps,
        order_no=order_no,
        supplier_name=supplier_name,
        item_name=item_name,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        order_status=order_status,
        applicant=applicant,
        remark=remark,
      )
    except PurchaseOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/local/purchase-orders/{order_id}')
  async def update_purchase_order(order_id: str, request: Request) -> Any:
    payload = await request.json()
    order_no = str(payload.get('orderNo', '')).strip()
    supplier_name = str(payload.get('supplierName', '')).strip()
    item_name = str(payload.get('itemName', '')).strip()
    quantity = safe_float_func(payload.get('quantity'), 0)
    unit_price = safe_float_func(payload.get('unitPrice'), 0)
    total_amount = safe_float_func(payload.get('totalAmount'), 0)
    order_status = safe_int_func(payload.get('status'), 0)
    applicant = str(payload.get('applicant', '')).strip() or '系统管理员'
    remark = str(payload.get('remark', '')).strip()

    try:
      update_purchase_order_command(
        deps,
        order_id=order_id,
        order_no=order_no,
        supplier_name=supplier_name,
        item_name=item_name,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        order_status=order_status,
        applicant=applicant,
        remark=remark,
      )
    except PurchaseOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/purchase-orders/{order_id}/submit')
  def submit_purchase_order(order_id: str) -> Any:
    try:
      submit_purchase_order_command(deps, order_id=order_id)
    except PurchaseOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/purchase-orders/{order_id}/approve')
  def approve_purchase_order(order_id: str, request: Request) -> Any:
    current_user = get_current_user_func(request)
    if not current_user:
      return fail_func('未登录或登录已过期', 401)
    user_id = str(current_user['user_id'])
    user_name = str(current_user['real_name'] or current_user['username'] or user_id)

    try:
      message = approve_purchase_order_command(deps, order_id=order_id, user_id=user_id, user_name=user_name)
    except PurchaseOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, message)

  @router.post('/local/purchase-orders/{order_id}/cancel')
  def cancel_purchase_order(order_id: str) -> Any:
    try:
      cancel_purchase_order_command(deps, order_id=order_id)
    except PurchaseOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/local/purchase-orders/{order_id}/approval-status')
  def get_purchase_order_approval_status(order_id: str) -> Any:
    try:
      return ok_func(get_purchase_order_approval_status_query(deps, order_id=order_id), 'success')
    except PurchaseOrderServiceError as error:
      return fail_func(error.message, error.code)

  @router.delete('/local/purchase-orders/{order_id}')
  def delete_purchase_order(order_id: str) -> Any:
    try:
      delete_purchase_order_command(deps, order_id=order_id)
    except PurchaseOrderServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
