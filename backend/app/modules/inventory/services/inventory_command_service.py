from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.inventory.deps import InventoryRouterDeps
from app.modules.inventory.repositories.inventory_item_repo import (
  delete_inventory_item as delete_inventory_item_row,
  fetch_inventory_item_for_transaction_by_id,
  fetch_inventory_item_for_transaction_by_sku,
  fetch_inventory_item_id,
  insert_inventory_item,
  update_inventory_item as update_inventory_item_row,
  update_inventory_item_stock,
)
from app.modules.inventory.repositories.inventory_transaction_repo import (
  count_inventory_transactions_by_item,
  insert_inventory_transaction,
)
from app.modules.inventory.services.errors import InventoryServiceError


def create_inventory_item(
  deps: InventoryRouterDeps,
  *,
  sku: str,
  item_name: str,
  unit: str,
  stock_qty: float,
  safety_qty: float,
) -> bool:
  if not sku or not item_name:
    raise InventoryServiceError('物料编码和物料名称不能为空', 400)
  if stock_qty < 0 or safety_qty < 0:
    raise InventoryServiceError('库存数量不能为负数', 400)

  now = deps.now_str_func()
  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    insert_inventory_item(
      cur,
      item_id=str(uuid.uuid4()),
      sku=sku,
      item_name=item_name,
      unit=unit,
      stock_qty=stock_qty,
      safety_qty=safety_qty,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise InventoryServiceError('物料编码已存在', 400) from error

  conn.close()
  return True


def update_inventory_item(
  deps: InventoryRouterDeps,
  *,
  item_id: str,
  sku: str,
  item_name: str,
  unit: str,
  stock_qty: float,
  safety_qty: float,
) -> bool:
  if not sku or not item_name:
    raise InventoryServiceError('物料编码和物料名称不能为空', 400)
  if stock_qty < 0 or safety_qty < 0:
    raise InventoryServiceError('库存数量不能为负数', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_inventory_item_id(cur, item_id)
  if not row:
    conn.close()
    raise InventoryServiceError('物料不存在', 404)

  try:
    update_inventory_item_row(
      cur,
      item_id=item_id,
      sku=sku,
      item_name=item_name,
      unit=unit,
      stock_qty=stock_qty,
      safety_qty=safety_qty,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise InventoryServiceError('物料编码已存在', 400) from error

  conn.close()
  return True


def delete_inventory_item(deps: InventoryRouterDeps, *, item_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_inventory_item_id(cur, item_id)
  if not row:
    conn.close()
    raise InventoryServiceError('物料不存在', 404)

  tx_cnt = deps.safe_int_func(count_inventory_transactions_by_item(cur, item_id)['cnt'], 0)
  if tx_cnt > 0:
    conn.close()
    raise InventoryServiceError('已有库存流水，不允许删除', 400)

  delete_inventory_item_row(cur, item_id)
  conn.commit()
  conn.close()
  return True


def create_inventory_transaction(
  deps: InventoryRouterDeps,
  *,
  item_id: str,
  sku: str,
  direction: int,
  quantity: float,
  business_no: str,
  operator_name: str,
  remark: str,
) -> bool:
  if direction not in (1, 2):
    raise InventoryServiceError('方向参数无效', 400)
  if quantity <= 0:
    raise InventoryServiceError('数量必须大于0', 400)
  if not item_id and not sku:
    raise InventoryServiceError('请提供物料ID或物料编码', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  item_row = fetch_inventory_item_for_transaction_by_id(cur, item_id) if item_id else fetch_inventory_item_for_transaction_by_sku(cur, sku)
  if not item_row:
    conn.close()
    raise InventoryServiceError('物料不存在', 404)

  stock_qty = deps.safe_float_func(item_row['stock_qty'], 0)
  if direction == 2 and stock_qty < quantity:
    conn.close()
    raise InventoryServiceError('出库数量超过当前库存', 400)

  new_stock = stock_qty + quantity if direction == 1 else stock_qty - quantity
  now = deps.now_str_func()
  try:
    update_inventory_item_stock(cur, item_id=str(item_row['id']), stock_qty=new_stock, now=now)
    insert_inventory_transaction(
      cur,
      transaction_id=str(uuid.uuid4()),
      item_id=str(item_row['id']),
      sku=str(item_row['sku']),
      item_name=str(item_row['item_name']),
      direction=direction,
      quantity=quantity,
      after_stock=new_stock,
      business_no=business_no,
      operator_name=operator_name,
      remark=remark,
      now=now,
    )
    conn.commit()
  except Exception as error:
    conn.rollback()
    conn.close()
    print('创建库存流水失败:', error)
    raise InventoryServiceError('创建库存流水失败', 500) from error

  conn.close()
  return True
