from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.quotation.deps import QuotationRouterDeps
from app.modules.quotation.helpers import generate_quote_no
from app.modules.quotation.services.errors import QuotationServiceError
from app.modules.quotation.services.quotation_command_service import (
  approve_quotation as approve_quotation_command,
  cancel_quotation as cancel_quotation_command,
  create_quotation as create_quotation_command,
  delete_quotation as delete_quotation_command,
  reject_quotation as reject_quotation_command,
  submit_quotation as submit_quotation_command,
  update_quotation as update_quotation_command,
)
from app.modules.quotation.services.quotation_query_service import (
  get_quotation_approval_status as get_quotation_approval_status_query,
  get_quotation_detail as get_quotation_detail_query,
  query_quotation_page,
)


def register_quotation_routes(router: APIRouter, deps: QuotationRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func
  safe_float_func = deps.safe_float_func
  get_current_user_func = deps.get_current_user_func

  @router.get('/local/quotations/page')
  def page_quotations(
    current: int = 1,
    size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(query_quotation_page(deps, current=current, size=size, keyword=keyword, status=status), 'success')

  @router.get('/local/quotations/{quotation_id}')
  def get_quotation_detail(quotation_id: str) -> Any:
    try:
      return ok_func(get_quotation_detail_query(deps, quotation_id=quotation_id), 'success')
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/local/quotations')
  async def create_quotation(request: Request) -> Any:
    payload = await request.json()
    quote_no = str(payload.get('quoteNo', '')).strip() or generate_quote_no()
    customer_id = str(payload.get('customerId', '')).strip()
    customer_name = str(payload.get('customerName', '')).strip()
    contact_person = str(payload.get('contactPerson', '')).strip()
    discount_rate = safe_float_func(payload.get('discountRate'), 100)
    validity_days = safe_int_func(payload.get('validityDays'), 30)
    validity_end_date = str(payload.get('validityEndDate', '')).strip()
    quote_status = safe_int_func(payload.get('status'), 0)
    remark = str(payload.get('remark', '')).strip()
    items = payload.get('items') if isinstance(payload.get('items'), list) else []
    current_user = get_current_user_func(request)
    applicant = str(payload.get('applicant', '')).strip() or (
      str(current_user['real_name'] or current_user['username']) if current_user else '系统管理员'
    )

    try:
      result = create_quotation_command(
        deps,
        quote_no=quote_no,
        customer_id=customer_id,
        customer_name=customer_name,
        contact_person=contact_person,
        discount_rate=discount_rate,
        validity_days=validity_days,
        validity_end_date=validity_end_date,
        quote_status=quote_status,
        applicant=applicant,
        version=safe_int_func(payload.get('version'), 1),
        remark=remark,
        items=items,
      )
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(result, 'success')

  @router.put('/local/quotations/{quotation_id}')
  async def update_quotation(quotation_id: str, request: Request) -> Any:
    payload = await request.json()
    quote_no = str(payload.get('quoteNo', '')).strip()
    customer_id = str(payload.get('customerId', '')).strip()
    customer_name = str(payload.get('customerName', '')).strip()
    contact_person = str(payload.get('contactPerson', '')).strip()
    discount_rate = safe_float_func(payload.get('discountRate'), 100)
    validity_days = safe_int_func(payload.get('validityDays'), 30)
    validity_end_date = str(payload.get('validityEndDate', '')).strip()
    quote_status = safe_int_func(payload.get('status'), 0)
    remark = str(payload.get('remark', '')).strip()
    items = payload.get('items') if isinstance(payload.get('items'), list) else []

    try:
      update_quotation_command(
        deps,
        quotation_id=quotation_id,
        quote_no=quote_no,
        customer_id=customer_id,
        customer_name=customer_name,
        contact_person=contact_person,
        discount_rate=discount_rate,
        validity_days=validity_days,
        validity_end_date=validity_end_date,
        quote_status=quote_status,
        remark=remark,
        items=items,
      )
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/quotations/{quotation_id}')
  def delete_quotation(quotation_id: str) -> Any:
    try:
      delete_quotation_command(deps, quotation_id=quotation_id)
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/quotations/{quotation_id}/submit')
  def submit_quotation(quotation_id: str) -> Any:
    try:
      submit_quotation_command(deps, quotation_id=quotation_id)
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/quotations/{quotation_id}/approve')
  def approve_quotation(quotation_id: str, request: Request) -> Any:
    current_user = get_current_user_func(request)
    if not current_user:
      return fail_func('未登录或登录已过期', 401)
    user_id = str(current_user['user_id'])
    user_name = str(current_user['real_name'] or current_user['username'] or user_id)

    try:
      approve_quotation_command(deps, quotation_id=quotation_id, user_id=user_id, user_name=user_name)
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/quotations/{quotation_id}/reject')
  def reject_quotation(quotation_id: str, request: Request, remark: str | None = None) -> Any:
    current_user = get_current_user_func(request)
    if not current_user:
      return fail_func('未登录或登录已过期', 401)
    user_id = str(current_user['user_id'])
    user_name = str(current_user['real_name'] or current_user['username'] or user_id)

    try:
      reject_quotation_command(
        deps,
        quotation_id=quotation_id,
        user_id=user_id,
        user_name=user_name,
        remark=str(remark or '').strip(),
      )
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/quotations/{quotation_id}/cancel')
  def cancel_quotation(quotation_id: str) -> Any:
    try:
      cancel_quotation_command(deps, quotation_id=quotation_id)
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/local/quotations/{quotation_id}/approval-status')
  def get_quotation_approval_status(quotation_id: str) -> Any:
    try:
      return ok_func(get_quotation_approval_status_query(deps, quotation_id=quotation_id), 'success')
    except QuotationServiceError as error:
      return fail_func(error.message, error.code)
