from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.product_catalog.deps import ProductCatalogRouterDeps
from app.modules.product_catalog.helpers import parse_product_catalog_payload
from app.modules.product_catalog.services.errors import ProductCatalogServiceError
from app.modules.product_catalog.services.product_catalog_command_service import (
  create_product_catalog as create_product_catalog_command,
  delete_product_catalog as delete_product_catalog_command,
  update_product_catalog as update_product_catalog_command,
)
from app.modules.product_catalog.services.product_catalog_query_service import (
  list_enabled_product_catalog,
  query_product_catalog_page,
)


def register_product_catalog_routes(router: APIRouter, deps: ProductCatalogRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func
  safe_int_func = deps.safe_int_func
  safe_float_func = deps.safe_float_func

  @router.get('/local/product-catalog/page')
  def page_product_catalog(
    current: int = 1,
    size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
  ) -> dict[str, Any]:
    return ok_func(query_product_catalog_page(deps, current=current, size=size, keyword=keyword, status=status), 'success')

  @router.get('/local/product-catalog/list')
  def list_product_catalog() -> dict[str, Any]:
    return ok_func(list_enabled_product_catalog(deps), 'success')

  @router.post('/local/product-catalog')
  async def create_product_catalog(request: Request) -> Any:
    payload = parse_product_catalog_payload(await request.json(), safe_int_func, safe_float_func)
    try:
      create_product_catalog_command(
        deps,
        product_code=payload['product_code'],
        product_name=payload['product_name'],
        specification=payload['specification'],
        unit=payload['unit'],
        reference_price=payload['reference_price'],
        cost_price=payload['cost_price'],
        category=payload['category'],
        status=payload['status'],
        remark=payload['remark'],
      )
    except ProductCatalogServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.put('/local/product-catalog/{product_id}')
  async def update_product_catalog(product_id: str, request: Request) -> Any:
    payload = parse_product_catalog_payload(await request.json(), safe_int_func, safe_float_func)
    try:
      update_product_catalog_command(
        deps,
        product_id=product_id,
        product_code=payload['product_code'],
        product_name=payload['product_name'],
        specification=payload['specification'],
        unit=payload['unit'],
        reference_price=payload['reference_price'],
        cost_price=payload['cost_price'],
        category=payload['category'],
        status=payload['status'],
        remark=payload['remark'],
      )
    except ProductCatalogServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.delete('/local/product-catalog/{product_id}')
  def delete_product_catalog(product_id: str) -> dict[str, Any]:
    delete_product_catalog_command(deps, product_id=product_id)
    return ok_func(True, 'success')
