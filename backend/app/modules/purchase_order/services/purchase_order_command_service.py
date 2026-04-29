from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.purchase_order.deps import PurchaseOrderRouterDeps
from app.modules.purchase_order.helpers import is_user_allowed_for_node, resolve_purchase_approval_flow
from app.modules.purchase_order.repositories.purchase_order_approval_repo import (
  delete_purchase_order_approval_logs,
  fetch_approval_node,
  fetch_max_node_index,
  insert_purchase_order_approval_log,
)
from app.modules.purchase_order.repositories.purchase_order_repo import (
  delete_purchase_order as delete_purchase_order_row,
  fetch_purchase_order_approval_row,
  fetch_purchase_order_status_row,
  insert_purchase_order,
  update_purchase_order as update_purchase_order_row,
  update_purchase_order_approved,
  update_purchase_order_cancelled,
  update_purchase_order_current_node,
  update_purchase_order_submit_state,
)
from app.modules.purchase_order.services.errors import PurchaseOrderServiceError


def create_purchase_order(
  deps: PurchaseOrderRouterDeps,
  *,
  order_no: str,
  supplier_name: str,
  item_name: str,
  quantity: float,
  unit_price: float,
  total_amount: float,
  order_status: int,
  applicant: str,
  remark: str,
) -> bool:
  if not supplier_name or not item_name:
    raise PurchaseOrderServiceError('供应商和物料名称不能为空', 400)
  if quantity <= 0:
    raise PurchaseOrderServiceError('采购数量必须大于0', 400)
  if unit_price < 0:
    raise PurchaseOrderServiceError('单价不能为负数', 400)

  final_total = total_amount if total_amount > 0 else round(quantity * unit_price, 2)
  now = deps.now_str_func()
  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    insert_purchase_order(
      cur,
      order_id=str(uuid.uuid4()),
      order_no=order_no,
      supplier_name=supplier_name,
      item_name=item_name,
      quantity=quantity,
      unit_price=unit_price,
      total_amount=final_total,
      status=order_status,
      applicant=applicant,
      remark=remark,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise PurchaseOrderServiceError('采购单号已存在', 400) from error

  conn.close()
  return True


def update_purchase_order(
  deps: PurchaseOrderRouterDeps,
  *,
  order_id: str,
  order_no: str,
  supplier_name: str,
  item_name: str,
  quantity: float,
  unit_price: float,
  total_amount: float,
  order_status: int,
  applicant: str,
  remark: str,
) -> bool:
  if not order_no or not supplier_name or not item_name:
    raise PurchaseOrderServiceError('采购单号、供应商和物料名称不能为空', 400)
  if quantity <= 0:
    raise PurchaseOrderServiceError('采购数量必须大于0', 400)
  if unit_price < 0:
    raise PurchaseOrderServiceError('单价不能为负数', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_purchase_order_status_row(cur, order_id)
  if not row:
    conn.close()
    raise PurchaseOrderServiceError('采购单不存在', 404)
  if int(row['status'] or 0) in (2, 3):
    conn.close()
    raise PurchaseOrderServiceError('当前状态不允许编辑', 400)

  final_total = total_amount if total_amount > 0 else round(quantity * unit_price, 2)
  try:
    update_purchase_order_row(
      cur,
      order_id=order_id,
      order_no=order_no,
      supplier_name=supplier_name,
      item_name=item_name,
      quantity=quantity,
      unit_price=unit_price,
      total_amount=final_total,
      status=order_status,
      applicant=applicant,
      remark=remark,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise PurchaseOrderServiceError('采购单号已存在', 400) from error

  conn.close()
  return True


def submit_purchase_order(deps: PurchaseOrderRouterDeps, *, order_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_purchase_order_status_row(cur, order_id)
  if not row:
    conn.close()
    raise PurchaseOrderServiceError('采购单不存在', 404)
  if int(row['status'] or 0) != 0:
    conn.close()
    raise PurchaseOrderServiceError('仅草稿状态可提交审批', 400)

  flow_id, nodes = resolve_purchase_approval_flow(cur)
  if flow_id <= 0:
    conn.close()
    raise PurchaseOrderServiceError('未配置启用的采购审批规则，请先在“业务相关审批规则”中配置', 400)
  if not nodes:
    conn.close()
    raise PurchaseOrderServiceError('采购审批规则未配置节点，请先补充审批节点及审批人', 400)

  delete_purchase_order_approval_logs(cur, order_id)
  update_purchase_order_submit_state(
    cur,
    order_id=order_id,
    approval_flow_id=flow_id,
    current_node_index=deps.safe_int_func(nodes[0]['node_index'], 1),
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def approve_purchase_order(
  deps: PurchaseOrderRouterDeps,
  *,
  order_id: str,
  user_id: str,
  user_name: str,
) -> str:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_purchase_order_approval_row(cur, order_id)
  if not row:
    conn.close()
    raise PurchaseOrderServiceError('采购单不存在', 404)
  if int(row['status'] or 0) != 1:
    conn.close()
    raise PurchaseOrderServiceError('仅待审批状态可通过', 400)

  flow_id = deps.safe_int_func(row['approval_flow_id'], 0)
  current_node_index = deps.safe_int_func(row['current_node_index'], 0)
  if flow_id <= 0 or current_node_index <= 0:
    conn.close()
    raise PurchaseOrderServiceError('审批流程异常，请重新提交该采购单', 400)

  node = fetch_approval_node(cur, flow_id, current_node_index)
  if not node:
    conn.close()
    raise PurchaseOrderServiceError('未找到当前审批节点，请检查审批规则配置', 400)
  if not is_user_allowed_for_node(cur, node, user_id):
    conn.close()
    raise PurchaseOrderServiceError('当前用户不在本节点审批人范围内', 403)

  now = deps.now_str_func()
  insert_purchase_order_approval_log(
    cur,
    approval_log_id=str(uuid.uuid4()),
    order_id=order_id,
    approval_flow_id=flow_id,
    node_index=current_node_index,
    node_name=node['approval_node_name'] or '',
    approver_id=user_id,
    approver_name=user_name,
    action='approve',
    remark='',
    action_time=now,
  )

  max_node = deps.safe_int_func(fetch_max_node_index(cur, flow_id)['max_node'], current_node_index)
  if current_node_index < max_node:
    update_purchase_order_current_node(cur, order_id=order_id, current_node_index=current_node_index + 1, now=now)
    conn.commit()
    conn.close()
    return '当前节点审批通过，已流转到下一节点'

  update_purchase_order_approved(cur, order_id=order_id, now=now)
  conn.commit()
  conn.close()
  return '审批完成'


def cancel_purchase_order(deps: PurchaseOrderRouterDeps, *, order_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_purchase_order_status_row(cur, order_id)
  if not row:
    conn.close()
    raise PurchaseOrderServiceError('采购单不存在', 404)
  if int(row['status'] or 0) not in {0, 1}:
    conn.close()
    raise PurchaseOrderServiceError('仅草稿或待审批状态可作废', 400)

  update_purchase_order_cancelled(cur, order_id=order_id, now=deps.now_str_func())
  conn.commit()
  conn.close()
  return True


def delete_purchase_order(deps: PurchaseOrderRouterDeps, *, order_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_purchase_order_status_row(cur, order_id)
  if not row:
    conn.close()
    raise PurchaseOrderServiceError('采购单不存在', 404)
  if int(row['status'] or 0) != 0:
    conn.close()
    raise PurchaseOrderServiceError('仅草稿状态可删除', 400)

  delete_purchase_order_approval_logs(cur, order_id)
  delete_purchase_order_row(cur, order_id)
  conn.commit()
  conn.close()
  return True
