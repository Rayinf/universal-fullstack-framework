from __future__ import annotations

import uuid

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.helpers import (
  is_user_allowed_for_node,
  resolve_work_order_approval_flow,
  resolve_work_order_notify_users,
)
from app.modules.work_order.repositories.user_repo import fetch_user_ids_by_role
from app.modules.work_order.repositories.work_inbound_repo import count_work_inbounds_by_work_order
from app.modules.work_order.repositories.work_order_approval_repo import (
  delete_work_order_approval_logs,
  fetch_approval_flow_nodes,
  fetch_approval_node,
  insert_work_order_approval_log,
)
from app.modules.work_order.repositories.work_order_repo import (
  delete_work_order as delete_work_order_row,
  fetch_work_order_approval_row,
  fetch_work_order_edit_guard_row,
  fetch_work_order_status_row,
  fetch_work_order_submit_row,
  insert_work_order,
  update_work_order as update_work_order_row,
  update_work_order_approved,
  update_work_order_cancelled,
  update_work_order_current_node,
  update_work_order_rejected,
  update_work_order_submit_state,
)
from app.modules.work_order.repositories.work_report_repo import count_work_reports_by_work_order
from app.modules.work_order.services.errors import WorkOrderServiceError


def create_work_order(
  deps: WorkOrderRouterDeps,
  *,
  work_order_no: str,
  contract_id: str,
  contract_no: str,
  customer_name: str,
  product_id: str,
  product_code: str,
  product_name: str,
  plan_quantity: float,
  work_order_status: int,
  priority: int,
  planned_start_date: str,
  planned_end_date: str,
  applicant: str,
  remark: str,
) -> bool:
  if not product_name:
    raise WorkOrderServiceError('产品名称不能为空', 400)
  if plan_quantity <= 0:
    raise WorkOrderServiceError('计划数量必须大于0', 400)
  if work_order_status not in (0, 7):
    work_order_status = 0

  conn = deps.get_conn_func()
  cur = conn.cursor()
  now = deps.now_str_func()
  try:
    insert_work_order(
      cur,
      work_order_id=str(uuid.uuid4()),
      work_order_no=work_order_no,
      contract_id=contract_id,
      contract_no=contract_no,
      customer_name=customer_name,
      product_id=product_id,
      product_code=product_code,
      product_name=product_name,
      plan_quantity=plan_quantity,
      status=work_order_status,
      priority=priority,
      planned_start_date=planned_start_date,
      planned_end_date=planned_end_date,
      applicant=applicant,
      remark=remark,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise WorkOrderServiceError('工单号已存在', 400) from error
  except Exception as error:
    conn.rollback()
    conn.close()
    print('创建工单失败:', error)
    raise WorkOrderServiceError('创建工单失败', 500) from error

  conn.close()
  return True


def update_work_order(
  deps: WorkOrderRouterDeps,
  *,
  work_order_id: str,
  work_order_no: str,
  contract_id: str,
  contract_no: str,
  customer_name: str,
  product_id: str,
  product_code: str,
  product_name: str,
  plan_quantity: float,
  priority: int,
  planned_start_date: str,
  planned_end_date: str,
  remark: str,
) -> bool:
  if not work_order_no or not product_name:
    raise WorkOrderServiceError('工单号和产品名称不能为空', 400)
  if plan_quantity <= 0:
    raise WorkOrderServiceError('计划数量必须大于0', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  old_row = fetch_work_order_edit_guard_row(cur, work_order_id)
  if not old_row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  if deps.safe_int_func(old_row['status'], 0) not in (0, 6, 7):
    conn.close()
    raise WorkOrderServiceError('当前状态不允许编辑', 400)
  if plan_quantity < deps.safe_float_func(old_row['qualified_quantity'], 0):
    conn.close()
    raise WorkOrderServiceError('计划数量不能小于已合格数量', 400)
  if plan_quantity < deps.safe_float_func(old_row['inbound_quantity'], 0):
    conn.close()
    raise WorkOrderServiceError('计划数量不能小于已入库数量', 400)

  try:
    update_work_order_row(
      cur,
      work_order_id=work_order_id,
      work_order_no=work_order_no,
      contract_id=contract_id,
      contract_no=contract_no,
      customer_name=customer_name,
      product_id=product_id,
      product_code=product_code,
      product_name=product_name,
      plan_quantity=plan_quantity,
      priority=priority,
      planned_start_date=planned_start_date,
      planned_end_date=planned_end_date,
      remark=remark,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise WorkOrderServiceError('工单号已存在', 400) from error

  conn.close()
  return True


def delete_work_order(deps: WorkOrderRouterDeps, *, work_order_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_work_order_status_row(cur, work_order_id)
  if not row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  if deps.safe_int_func(row['status'], 0) not in (0, 6, 7):
    conn.close()
    raise WorkOrderServiceError('仅草稿/驳回/作废状态可删除', 400)

  if deps.safe_int_func(count_work_reports_by_work_order(cur, work_order_id)['cnt'], 0) > 0:
    conn.close()
    raise WorkOrderServiceError('已有报工记录，不允许删除', 400)
  if deps.safe_int_func(count_work_inbounds_by_work_order(cur, work_order_id)['cnt'], 0) > 0:
    conn.close()
    raise WorkOrderServiceError('已有入库记录，不允许删除', 400)

  delete_work_order_approval_logs(cur, work_order_id)
  delete_work_order_row(cur, work_order_id)
  conn.commit()
  conn.close()
  return True


def submit_work_order(deps: WorkOrderRouterDeps, *, work_order_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_work_order_submit_row(cur, work_order_id)
  if not row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  if deps.safe_int_func(row['status'], 0) != 0:
    conn.close()
    raise WorkOrderServiceError('仅草稿状态可提交审批', 400)

  flow_id, nodes = resolve_work_order_approval_flow(cur, deps.safe_int_func)
  if flow_id <= 0:
    conn.close()
    raise WorkOrderServiceError('未配置启用的工单审批规则，请先在审批规则中配置 approval_type=5', 400)
  if not nodes:
    conn.close()
    raise WorkOrderServiceError('工单审批规则未配置节点', 400)

  first_node_index = deps.safe_int_func(nodes[0]['node_index'], 1)
  delete_work_order_approval_logs(cur, work_order_id)
  update_work_order_submit_state(
    cur,
    work_order_id=work_order_id,
    approval_flow_id=flow_id,
    current_node_index=first_node_index,
    now=deps.now_str_func(),
  )

  first_node = nodes[0]
  notify_user_ids: list[str] = []
  approval_ids = str(first_node['approval_ids'] or '').strip()
  if approval_ids:
    notify_user_ids = [uid.strip() for uid in approval_ids.split(',') if uid.strip()]
  else:
    role_id = str(first_node['role_id'] or '').strip()
    if role_id:
      notify_user_ids = fetch_user_ids_by_role(cur, role_id)

  conn.commit()
  conn.close()
  if notify_user_ids:
    deps.create_notification_for_users_func(
      notify_user_ids,
      title='生产工单待审批',
      content=f'生产工单 {work_order_id} 已提交审批，请尽快处理',
      ntype=1,
      biz_type='work_order',
      biz_id=work_order_id,
    )
  return True


def approve_work_order(
  deps: WorkOrderRouterDeps,
  *,
  work_order_id: str,
  user_id: str,
  user_name: str,
) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_work_order_approval_row(cur, work_order_id)
  if not row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  if deps.safe_int_func(row['status'], 0) != 1:
    conn.close()
    raise WorkOrderServiceError('仅待审批状态可通过', 400)

  flow_id = deps.safe_int_func(row['approval_flow_id'], 0)
  current_node_index = deps.safe_int_func(row['current_node_index'], 0)
  if flow_id <= 0 or current_node_index <= 0:
    conn.close()
    raise WorkOrderServiceError('审批流程异常，请重新提交该工单', 400)

  node = fetch_approval_node(cur, flow_id, current_node_index)
  if not node:
    conn.close()
    raise WorkOrderServiceError('未找到当前审批节点，请检查审批规则配置', 400)
  if not is_user_allowed_for_node(cur, node, user_id):
    conn.close()
    raise WorkOrderServiceError('当前用户不在本节点审批人范围内', 403)

  now = deps.now_str_func()
  insert_work_order_approval_log(
    cur,
    approval_log_id=str(uuid.uuid4()),
    work_order_id=work_order_id,
    approval_flow_id=flow_id,
    node_index=current_node_index,
    node_name=node['approval_node_name'] or '',
    approver_id=user_id,
    approver_name=user_name,
    action='approve',
    remark='',
    action_time=now,
  )
  node_indexes = [deps.safe_int_func(row_item['node_index'], 0) for row_item in fetch_approval_flow_nodes(cur, flow_id)]
  current_pos = -1
  for idx, node_idx in enumerate(node_indexes):
    if node_idx == current_node_index:
      current_pos = idx
      break

  if current_pos < 0:
    conn.rollback()
    conn.close()
    raise WorkOrderServiceError('审批节点顺序异常，请检查审批规则配置', 400)

  if current_pos >= len(node_indexes) - 1:
    update_work_order_approved(cur, work_order_id=work_order_id, now=now)
  else:
    next_node_index = node_indexes[current_pos + 1]
    update_work_order_current_node(cur, work_order_id=work_order_id, current_node_index=next_node_index, now=now)

  conn.commit()
  conn.close()
  return True


def reject_work_order(
  deps: WorkOrderRouterDeps,
  *,
  work_order_id: str,
  user_id: str,
  user_name: str,
  remark: str,
) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_work_order_approval_row(cur, work_order_id)
  if not row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  if deps.safe_int_func(row['status'], 0) != 1:
    conn.close()
    raise WorkOrderServiceError('仅待审批状态可驳回', 400)

  flow_id = deps.safe_int_func(row['approval_flow_id'], 0)
  current_node_index = deps.safe_int_func(row['current_node_index'], 0)
  node = fetch_approval_node(cur, flow_id, current_node_index)
  if not node:
    conn.close()
    raise WorkOrderServiceError('未找到当前审批节点', 400)
  if not is_user_allowed_for_node(cur, node, user_id):
    conn.close()
    raise WorkOrderServiceError('当前用户不在本节点审批人范围内', 403)

  now = deps.now_str_func()
  insert_work_order_approval_log(
    cur,
    approval_log_id=str(uuid.uuid4()),
    work_order_id=work_order_id,
    approval_flow_id=flow_id,
    node_index=current_node_index,
    node_name=node['approval_node_name'] or '',
    approver_id=user_id,
    approver_name=user_name,
    action='reject',
    remark=remark,
    action_time=now,
  )
  update_work_order_rejected(cur, work_order_id=work_order_id, now=now)
  notify_user_ids = resolve_work_order_notify_users(cur, str(row['applicant'] or ''))
  work_order_no = str(row['work_order_no'] or work_order_id)
  conn.commit()
  conn.close()
  if notify_user_ids:
    deps.create_notification_for_users_func(
      notify_user_ids,
      title='生产工单审批驳回',
      content=f'生产工单 {work_order_no} 已被驳回，请及时处理',
      ntype=2,
      biz_type='work_order',
      biz_id=work_order_id,
    )
  return True


def cancel_work_order(deps: WorkOrderRouterDeps, *, work_order_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_work_order_status_row(cur, work_order_id)
  if not row:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  if deps.safe_int_func(row['status'], 0) not in (0, 1, 6):
    conn.close()
    raise WorkOrderServiceError('仅草稿/待审批/已驳回状态可作废', 400)

  update_work_order_cancelled(cur, work_order_id=work_order_id, now=deps.now_str_func())
  conn.commit()
  conn.close()
  return True
