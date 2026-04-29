from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.services.commission_command_service import (
  calculate_commission as calculate_commission_command,
  delete_commission as delete_commission_command,
  pay_commission as pay_commission_command,
)
from app.modules.contracts.services.commission_query_service import (
  export_commission_rows,
  get_commission_summary,
  query_commission_page,
)
from app.modules.contracts.services.errors import ContractServiceError


def register_commission_routes(router: APIRouter, deps: ContractRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  now_str_func = deps.now_str_func
  safe_float_func = deps.safe_float_func
  export_to_excel_func = deps.export_to_excel_func

  @router.get('/local/commissions/page')
  def page_commissions(
    current: int = 1,
    size: int = 10,
    status: int | None = None,
    salespersonName: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_commission_page(
        deps,
        current=current,
        size=size,
        status=status,
        salesperson_name=salespersonName,
      ),
      'success',
    )

  @router.get('/local/commissions/export')
  def export_commissions(status: int | None = None, salespersonName: str | None = None) -> Any:
    headers, data_rows, sheet_name = export_commission_rows(deps, status=status, salesperson_name=salespersonName)
    return export_to_excel_func(headers, data_rows, sheet_name)

  @router.post('/local/commissions/calculate/{contract_id}')
  async def calculate_commission(contract_id: str, request: Request) -> Any:
    payload = await request.json()
    salesperson_id = str(payload.get('salespersonId', '')).strip()
    salesperson_name = str(payload.get('salespersonName', '')).strip()
    commission_rate = safe_float_func(payload.get('commissionRate'), 0)
    remark = str(payload.get('remark', '')).strip()

    try:
      result = calculate_commission_command(
        deps,
        contract_id=contract_id,
        salesperson_id=salesperson_id,
        salesperson_name=salesperson_name,
        commission_rate=commission_rate,
        remark=remark,
      )
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(result, 'success')

  @router.post('/local/commissions/{commission_id}/pay')
  def pay_commission(commission_id: str, payDate: str | None = None) -> Any:
    try:
      pay_commission_command(deps, commission_id=commission_id, pay_date=str(payDate or now_str_func())[:10])
    except ContractServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/commissions/{commission_id}')
  def delete_commission(commission_id: str) -> dict[str, Any]:
    delete_commission_command(deps, commission_id=commission_id)
    return ok_func(True, 'success')

  @router.get('/local/commissions/summary')
  def commission_summary() -> dict[str, Any]:
    return ok_func(get_commission_summary(deps), 'success')
