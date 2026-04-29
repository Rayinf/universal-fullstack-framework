from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.helpers import resolve_work_order_notify_users
from app.modules.work_order.repositories.inventory_repo import (
  fetch_inventory_item_by_sku,
  insert_inventory_item,
  insert_inventory_transaction,
  update_inventory_item_stock,
)
from app.modules.work_order.repositories.work_inbound_repo import insert_work_inbound
from app.modules.work_order.repositories.work_order_repo import (
  complete_work_order,
  fetch_work_order_for_inbound,
  fetch_work_order_quantity_row,
  increment_work_order_inbound_quantity,
)
from app.modules.work_order.services.errors import WorkOrderServiceError


def create_work_inbound(
  deps: WorkOrderRouterDeps,
  *,
  work_order_id: str,
  inbound_no: str,
  quantity: float,
  warehouse_name: str,
  operator_name: str,
  inbound_time: str,
  remark: str,
) -> bool:
  if not work_order_id:
    raise WorkOrderServiceError('请选择生产工单', 400)
  if quantity <= 0:
    raise WorkOrderServiceError('入库数量必须大于0', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  work_order = fetch_work_order_for_inbound(cur, work_order_id)
  if not work_order:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)

  work_order_status = deps.safe_int_func(work_order['status'], 0)
  if work_order_status not in (3, 4, 5):
    conn.close()
    raise WorkOrderServiceError('当前工单状态不允许入库', 400)

  qualified_quantity = deps.safe_float_func(work_order['qualified_quantity'], 0)
  inbound_quantity = deps.safe_float_func(work_order['inbound_quantity'], 0)
  remain = qualified_quantity - inbound_quantity
  if remain <= 0:
    conn.close()
    raise WorkOrderServiceError('该工单无可入库数量', 400)
  if quantity > remain + 0.0001:
    conn.close()
    raise WorkOrderServiceError('入库数量超过可入库数量', 400)

  now = deps.now_str_func()
  sku = str(work_order['product_code'] or '').strip() or str(work_order['work_order_no'] or '').strip()
  item_name = str(work_order['product_name'] or '成品')
  notify_user_ids: list[str] = []
  should_notify_completed = False
  try:
    insert_work_inbound(
      cur,
      inbound_id=str(uuid.uuid4()),
      inbound_no=inbound_no,
      work_order_id=work_order_id,
      work_order_no=str(work_order['work_order_no']),
      quantity=quantity,
      warehouse_name=warehouse_name,
      operator_name=operator_name,
      inbound_time=inbound_time,
      remark=remark,
      create_time=now,
    )

    item_row = fetch_inventory_item_by_sku(cur, sku)
    if item_row:
      item_id = str(item_row['id'])
      old_stock = deps.safe_float_func(item_row['stock_qty'], 0)
      new_stock = old_stock + quantity
      update_inventory_item_stock(cur, item_id=item_id, stock_qty=new_stock, now=now)
    else:
      item_id = str(uuid.uuid4())
      new_stock = quantity
      insert_inventory_item(
        cur,
        item_id=item_id,
        sku=sku,
        item_name=item_name,
        unit='pcs',
        stock_qty=new_stock,
        create_time=now,
        update_time=now,
      )

    insert_inventory_transaction(
      cur,
      transaction_id=str(uuid.uuid4()),
      item_id=item_id,
      sku=sku,
      item_name=item_name,
      direction=1,
      quantity=quantity,
      after_stock=new_stock,
      business_no=inbound_no,
      operator_name=operator_name,
      remark=f'生产工单入库:{str(work_order["work_order_no"])}',
      create_time=now,
    )

    increment_work_order_inbound_quantity(cur, work_order_id=work_order_id, quantity=quantity, now=now)
    refreshed = fetch_work_order_quantity_row(cur, work_order_id)
    if refreshed and deps.safe_float_func(refreshed['qualified_quantity'], 0) > 0 and deps.safe_float_func(refreshed['inbound_quantity'], 0) >= deps.safe_float_func(refreshed['qualified_quantity'], 0):
      complete_work_order(cur, work_order_id=work_order_id, now=now)
      should_notify_completed = True
      notify_user_ids = resolve_work_order_notify_users(cur, str(work_order['applicant'] or ''))

    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise WorkOrderServiceError('入库单号已存在', 400) from error
  except Exception as error:
    conn.rollback()
    conn.close()
    print('新增完工入库失败:', error)
    raise WorkOrderServiceError('新增完工入库失败', 500) from error

  conn.close()
  if should_notify_completed and notify_user_ids:
    deps.create_notification_for_users_func(
      notify_user_ids,
      title='生产工单已完结',
      content=f'生产工单 {str(work_order["work_order_no"])} 已完成并全部入库',
      ntype=1,
      biz_type='work_order',
      biz_id=work_order_id,
    )
  return True
