from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.inventory.deps import InventoryRouterDeps
from app.modules.inventory.helpers import parse_inventory_item_payload, parse_inventory_transaction_payload
from app.modules.inventory.services.errors import InventoryServiceError
from app.modules.inventory.services.inventory_command_service import (
  create_inventory_item as create_inventory_item_command,
  create_inventory_transaction as create_inventory_transaction_command,
  delete_inventory_item as delete_inventory_item_command,
  update_inventory_item as update_inventory_item_command,
)
from app.modules.inventory.services.inventory_query_service import (
  query_inventory_item_page,
  query_inventory_summary,
  query_inventory_transaction_page,
)


def register_inventory_routes(router: APIRouter, deps: InventoryRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_float_func = deps.safe_float_func
  safe_int_func = deps.safe_int_func

  @router.get('/local/inventory/items/page')
  def page_inventory_items(current: int = 1, size: int = 10, keyword: str | None = None) -> dict[str, Any]:
    return ok_func(query_inventory_item_page(deps, current=current, size=size, keyword=keyword), 'success')

  @router.post('/local/inventory/items')
  async def create_inventory_item(request: Request) -> Any:
    payload = parse_inventory_item_payload(await request.json(), safe_float_func)
    try:
      create_inventory_item_command(
        deps,
        sku=payload['sku'],
        item_name=payload['item_name'],
        unit=payload['unit'],
        stock_qty=payload['stock_qty'],
        safety_qty=payload['safety_qty'],
      )
    except InventoryServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/local/inventory/items/{item_id}')
  async def update_inventory_item(item_id: str, request: Request) -> Any:
    payload = parse_inventory_item_payload(await request.json(), safe_float_func)
    try:
      update_inventory_item_command(
        deps,
        item_id=item_id,
        sku=payload['sku'],
        item_name=payload['item_name'],
        unit=payload['unit'],
        stock_qty=payload['stock_qty'],
        safety_qty=payload['safety_qty'],
      )
    except InventoryServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/inventory/items/{item_id}')
  def delete_inventory_item(item_id: str) -> Any:
    try:
      delete_inventory_item_command(deps, item_id=item_id)
    except InventoryServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/local/inventory/summary')
  def get_inventory_summary(keyword: str | None = None, lowStockOnly: int | None = None) -> dict[str, Any]:
    return ok_func(query_inventory_summary(deps, keyword=keyword, low_stock_only=lowStockOnly), 'success')

  @router.get('/local/inventory/transactions/page')
  def page_inventory_transactions(
    current: int = 1,
    size: int = 10,
    keyword: str | None = None,
    direction: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(
      query_inventory_transaction_page(deps, current=current, size=size, keyword=keyword, direction=direction),
      'success',
    )

  @router.post('/local/inventory/transactions')
  async def create_inventory_transaction(request: Request) -> Any:
    payload = parse_inventory_transaction_payload(await request.json(), safe_int_func, safe_float_func)
    try:
      create_inventory_transaction_command(
        deps,
        item_id=payload['item_id'],
        sku=payload['sku'],
        direction=payload['direction'],
        quantity=payload['quantity'],
        business_no=payload['business_no'],
        operator_name=payload['operator_name'],
        remark=payload['remark'],
      )
    except InventoryServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')
