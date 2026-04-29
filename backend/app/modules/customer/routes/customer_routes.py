from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.customer.deps import CustomerRouterDeps
from app.modules.customer.helpers import parse_customer_payload
from app.modules.customer.services.customer_command_service import (
  create_customer as create_customer_command,
  delete_customer as delete_customer_command,
  update_customer as update_customer_command,
)
from app.modules.customer.services.customer_query_service import (
  get_customer_by_id as get_customer_by_id_query,
  query_customer_list,
  query_customer_page,
)
from app.modules.customer.services.errors import CustomerServiceError


def register_customer_routes(router: APIRouter, deps: CustomerRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func

  @router.get('/manage/api/customers/page')
  def page_customers(
    current: int = 1,
    size: int = 10,
    customerCode: str | None = None,
    searchKey: str | None = None,
    customerLevel: int | None = None,
    startDate: str | None = None,
    endDate: str | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_customer_page(
        deps,
        current=current,
        size=size,
        customer_code=customerCode,
        search_key=searchKey,
        customer_level=customerLevel,
        start_date=startDate,
        end_date=endDate,
      ),
      'success',
    )

  @router.get('/manage/api/customers/list')
  def list_customers() -> dict[str, Any]:
    return ok_func(query_customer_list(deps), 'success')

  @router.get('/manage/api/customers/{customer_id}')
  def get_customer_by_id(customer_id: str) -> Any:
    try:
      result = get_customer_by_id_query(deps, customer_id=customer_id)
    except CustomerServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(result, 'success')

  @router.post('/manage/api/customers/save')
  async def save_customer(request: Request) -> Any:
    payload = parse_customer_payload(await request.json(), safe_int_func)
    try:
      create_customer_command(
        deps,
        customer_code=payload['customer_code'],
        customer_name=payload['customer_name'],
        account_manager_name=payload['account_manager_name'],
        introducer_name=payload['introducer_name'],
        customer_level=payload['customer_level'],
        special_notes=payload['special_notes'],
      )
    except CustomerServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.post('/manage/api/customers/update')
  async def update_customer(request: Request) -> Any:
    payload = parse_customer_payload(await request.json(), safe_int_func)
    try:
      update_customer_command(
        deps,
        customer_id=payload['customer_id'],
        customer_code=payload['customer_code'],
        customer_name=payload['customer_name'],
        account_manager_name=payload['account_manager_name'],
        introducer_name=payload['introducer_name'],
        customer_level=payload['customer_level'],
        special_notes=payload['special_notes'],
      )
    except CustomerServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/manage/api/customers/{customer_id}')
  def delete_customer(customer_id: str) -> dict[str, Any]:
    delete_customer_command(deps, customer_id=customer_id)
    return ok_func(True, 'success')
