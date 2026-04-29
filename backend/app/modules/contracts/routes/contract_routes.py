from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.helpers import generate_contract_no
from app.modules.contracts.services.contract_command_service import (
  check_expiring_contracts as check_expiring_contracts_command,
  create_contract as create_contract_command,
  create_contract_from_quotation as create_contract_from_quotation_command,
  delete_contract as delete_contract_command,
  terminate_contract as terminate_contract_command,
  update_contract as update_contract_command,
)
from app.modules.contracts.services.contract_query_service import (
  export_contract_rows,
  get_contract_dashboard,
  get_contract_detail as get_contract_detail_query,
  get_contract_payment_summary,
  query_contract_page,
)
from app.modules.contracts.services.errors import ContractServiceError


def register_contract_routes(router: APIRouter, deps: ContractRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func
  safe_float_func = deps.safe_float_func
  export_to_excel_func = deps.export_to_excel_func

  @router.get('/local/contracts/page')
  def page_contracts(
    current: int = 1,
    size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(query_contract_page(deps, current=current, size=size, keyword=keyword, status=status), 'success')

  @router.get('/local/contracts/export')
  def export_contracts(keyword: str | None = None, status: int | None = None) -> Any:
    headers, data_rows, sheet_name = export_contract_rows(deps, keyword=keyword, status=status)
    return export_to_excel_func(headers, data_rows, sheet_name)

  @router.get('/local/contracts/{contract_id}')
  def get_contract_detail(contract_id: str) -> Any:
    try:
      return ok_func(get_contract_detail_query(deps, contract_id=contract_id), 'success')
    except ContractServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/local/contracts')
  async def create_contract(request: Request) -> Any:
    payload = await request.json()
    contract_no = str(payload.get('contractNo', '')).strip() or generate_contract_no()
    quotation_id = str(payload.get('quotationId', '')).strip()
    customer_id = str(payload.get('customerId', '')).strip()
    customer_name = str(payload.get('customerName', '')).strip()
    contract_name = str(payload.get('contractName', '')).strip()
    total_amount = safe_float_func(payload.get('totalAmount'), 0)
    signed_date = str(payload.get('signedDate', '')).strip()
    start_date = str(payload.get('startDate', '')).strip()
    end_date = str(payload.get('endDate', '')).strip()
    payment_terms = str(payload.get('paymentTerms', '')).strip()
    contract_status = safe_int_func(payload.get('status'), 0)
    remark = str(payload.get('remark', '')).strip()

    try:
      create_contract_command(
        deps,
        contract_no=contract_no,
        quotation_id=quotation_id,
        customer_id=customer_id,
        customer_name=customer_name,
        contract_name=contract_name,
        total_amount=total_amount,
        signed_date=signed_date,
        start_date=start_date,
        end_date=end_date,
        payment_terms=payment_terms,
        contract_status=contract_status,
        remark=remark,
      )
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/contracts/from-quotation/{quotation_id}')
  async def create_contract_from_quotation(quotation_id: str, request: Request) -> Any:
    try:
      body = await request.json()
    except Exception:
      body = {}

    contract_name = str(body.get('contractName', '')).strip()
    payment_terms = str(body.get('paymentTerms', '')).strip()
    signed_date = str(body.get('signedDate', '')).strip()
    start_date = str(body.get('startDate', '')).strip()
    end_date = str(body.get('endDate', '')).strip()
    try:
      result = create_contract_from_quotation_command(
        deps,
        quotation_id=quotation_id,
        contract_name=contract_name,
        payment_terms=payment_terms,
        signed_date=signed_date,
        start_date=start_date,
        end_date=end_date,
      )
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(result, 'success')

  @router.put('/local/contracts/{contract_id}')
  async def update_contract(contract_id: str, request: Request) -> Any:
    payload = await request.json()
    contract_no = str(payload.get('contractNo', '')).strip()
    customer_id = str(payload.get('customerId', '')).strip()
    customer_name = str(payload.get('customerName', '')).strip()
    contract_name = str(payload.get('contractName', '')).strip()
    total_amount = safe_float_func(payload.get('totalAmount'), 0)
    signed_date = str(payload.get('signedDate', '')).strip()
    start_date = str(payload.get('startDate', '')).strip()
    end_date = str(payload.get('endDate', '')).strip()
    payment_terms = str(payload.get('paymentTerms', '')).strip()
    contract_status = safe_int_func(payload.get('status'), 0)
    remark = str(payload.get('remark', '')).strip()

    if not contract_no or not customer_name or not contract_name:
      return fail_func('合同编号、客户名称、合同名称不能为空', 400)

    try:
      update_contract_command(
        deps,
        contract_id=contract_id,
        contract_no=contract_no,
        customer_id=customer_id,
        customer_name=customer_name,
        contract_name=contract_name,
        total_amount=total_amount,
        signed_date=signed_date,
        start_date=start_date,
        end_date=end_date,
        payment_terms=payment_terms,
        contract_status=contract_status,
        remark=remark,
      )
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/contracts/{contract_id}')
  def delete_contract(contract_id: str) -> Any:
    try:
      delete_contract_command(deps, contract_id=contract_id)
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/local/contracts/{contract_id}/terminate')
  def terminate_contract(contract_id: str, remark: str | None = None) -> Any:
    try:
      terminate_contract_command(deps, contract_id=contract_id, remark=str(remark or '').strip())
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/local/contracts/payment-summary')
  def contract_payment_summary(contractId: str | None = None) -> dict[str, Any]:
    return ok_func(get_contract_payment_summary(deps, contract_id=contractId), 'success')

  @router.get('/local/contracts/check-expiring')
  def check_expiring_contracts(days: int = 30) -> dict[str, Any]:
    return ok_func(check_expiring_contracts_command(deps, days=days), 'success')

  @router.get('/local/contract/dashboard')
  def contract_dashboard() -> dict[str, Any]:
    return ok_func(get_contract_dashboard(deps), 'success')
