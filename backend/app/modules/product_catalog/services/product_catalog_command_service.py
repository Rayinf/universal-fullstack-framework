from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.product_catalog.deps import ProductCatalogRouterDeps
from app.modules.product_catalog.repositories.product_catalog_repo import (
  delete_product_catalog as delete_product_catalog_row,
  insert_product_catalog,
  update_product_catalog as update_product_catalog_row,
)
from app.modules.product_catalog.services.errors import ProductCatalogServiceError


def create_product_catalog(
  deps: ProductCatalogRouterDeps,
  *,
  product_code: str,
  product_name: str,
  specification: str,
  unit: str,
  reference_price: float,
  cost_price: float,
  category: str,
  status: int,
  remark: str,
) -> bool:
  if not product_code or not product_name:
    raise ProductCatalogServiceError('产品编码和产品名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    insert_product_catalog(
      cur,
      product_id=str(uuid.uuid4()),
      product_code=product_code,
      product_name=product_name,
      specification=specification,
      unit=unit,
      reference_price=reference_price,
      cost_price=cost_price,
      category=category,
      status=status,
      remark=remark,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ProductCatalogServiceError('产品编码已存在', 400) from error

  conn.close()
  return True


def update_product_catalog(
  deps: ProductCatalogRouterDeps,
  *,
  product_id: str,
  product_code: str,
  product_name: str,
  specification: str,
  unit: str,
  reference_price: float,
  cost_price: float,
  category: str,
  status: int,
  remark: str,
) -> bool:
  if not product_code or not product_name:
    raise ProductCatalogServiceError('产品编码和产品名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    update_product_catalog_row(
      cur,
      product_id=product_id,
      product_code=product_code,
      product_name=product_name,
      specification=specification,
      unit=unit,
      reference_price=reference_price,
      cost_price=cost_price,
      category=category,
      status=status,
      remark=remark,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise ProductCatalogServiceError('产品编码已存在', 400) from error

  conn.close()
  return True


def delete_product_catalog(deps: ProductCatalogRouterDeps, *, product_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  delete_product_catalog_row(cur, product_id)
  conn.commit()
  conn.close()
  return True
