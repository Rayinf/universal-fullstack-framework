from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.helpers import generate_payment_no
from app.modules.contracts.services.errors import ContractServiceError
from app.modules.contracts.services.payment_command_service import (
  confirm_payment as confirm_payment_command,
  create_payment as create_payment_command,
  delete_payment as delete_payment_command,
)
from app.modules.contracts.services.payment_query_service import export_payment_rows, query_payment_page


def register_payment_routes(router: APIRouter, deps: ContractRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  now_str_func = deps.now_str_func
  safe_int_func = deps.safe_int_func
  safe_float_func = deps.safe_float_func
  get_current_user_func = deps.get_current_user_func
  export_to_excel_func = deps.export_to_excel_func

  @router.get('/local/payments/page')
  def page_payments(
    current: int = 1,
    size: int = 10,
    contractId: str | None = None,
    status: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(query_payment_page(deps, current=current, size=size, contract_id=contractId, status=status), 'success')

  @router.get('/local/payments/export')
  def export_payments(contractId: str | None = None, status: int | None = None) -> Any:
    headers, data_rows, sheet_name = export_payment_rows(deps, contract_id=contractId, status=status)
    return export_to_excel_func(headers, data_rows, sheet_name)

  @router.post('/local/payments')
  async def create_payment(request: Request) -> Any:
    payload = await request.json()
    contract_id = str(payload.get('contractId', '')).strip()
    payment_no = str(payload.get('paymentNo', '')).strip() or generate_payment_no()
    payment_amount = safe_float_func(payload.get('paymentAmount'), 0)
    payment_date = str(payload.get('paymentDate', '')).strip()
    payment_method = safe_int_func(payload.get('paymentMethod'), 1)
    payer_name = str(payload.get('payerName', '')).strip()
    remark = str(payload.get('remark', '')).strip()
    current_user = get_current_user_func(request)
    received_by = str(payload.get('receivedBy', '')).strip() or (
      str(current_user['real_name'] or current_user['username']) if current_user else '系统管理员'
    )

    try:
      create_payment_command(
        deps,
        contract_id=contract_id,
        payment_no=payment_no,
        payment_amount=payment_amount,
        payment_date=payment_date,
        payment_method=payment_method,
        payer_name=payer_name,
        received_by=received_by,
        remark=remark,
      )
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/payments/{payment_id}/confirm')
  def confirm_payment(payment_id: str) -> Any:
    try:
      confirm_payment_command(deps, payment_id=payment_id)
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/payments/{payment_id}')
  def delete_payment(payment_id: str) -> Any:
    try:
      delete_payment_command(deps, payment_id=payment_id)
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
