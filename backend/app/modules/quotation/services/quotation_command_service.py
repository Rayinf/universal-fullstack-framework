from __future__ import annotations

import uuid
from typing import Any

from app.infra.db_errors import DatabaseIntegrityError
from app.modules.quotation.deps import QuotationRouterDeps
from app.modules.quotation.helpers import (
  is_user_allowed_for_node,
  resolve_quotation_approval_flow,
  save_quotation_items,
)
from app.modules.quotation.repositories.quotation_approval_repo import (
  delete_quotation_approval_logs,
  fetch_approval_flow_nodes,
  fetch_approval_node,
  insert_quotation_approval_log,
)
from app.modules.quotation.repositories.quotation_item_repo import delete_quotation_items
from app.modules.quotation.repositories.quotation_repo import (
  delete_quotation as delete_quotation_row,
  fetch_quotation_approval_row,
  fetch_quotation_edit_guard_row,
  fetch_quotation_status_row,
  fetch_quotation_submit_row,
  insert_quotation,
  update_quotation as update_quotation_row,
  update_quotation_approved,
  update_quotation_cancelled,
  update_quotation_current_node,
  update_quotation_rejected,
  update_quotation_submit_state,
)
from app.modules.quotation.repositories.user_repo import fetch_user_ids_by_role
from app.modules.quotation.services.errors import QuotationServiceError


def create_quotation(
  deps: QuotationRouterDeps,
  *,
  quote_no: str,
  customer_id: str,
  customer_name: str,
  contact_person: str,
  discount_rate: float,
  validity_days: int,
  validity_end_date: str,
  quote_status: int,
  applicant: str,
  version: int,
  remark: str,
  items: list[dict[str, Any]],
) -> dict[str, str]:
  if not customer_name:
    raise QuotationServiceError('客户名称不能为空', 400)
  if not items:
    raise QuotationServiceError('报价明细不能为空', 400)

  quotation_id = str(uuid.uuid4())
  now = deps.now_str_func()
  conn = deps.get_conn_func()
  cur = conn.cursor()
  try:
    total_amount = save_quotation_items(cur, quotation_id, items, deps.safe_float_func, deps.safe_int_func)
    final_amount = round(total_amount * discount_rate / 100, 2)
    insert_quotation(
      cur,
      quotation_id=quotation_id,
      quote_no=quote_no,
      customer_id=customer_id,
      customer_name=customer_name,
      contact_person=contact_person,
      total_amount=total_amount,
      discount_rate=discount_rate,
      final_amount=final_amount,
      validity_days=validity_days,
      validity_end_date=validity_end_date,
      status=quote_status,
      applicant=applicant,
      version=version,
      remark=remark,
      now=now,
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise QuotationServiceError('报价单号已存在', 400) from error
  except Exception as error:
    conn.rollback()
    conn.close()
    print('创建报价单失败:', error)
    raise QuotationServiceError('创建报价单失败', 500) from error

  conn.close()
  return {'id': quotation_id}


def update_quotation(
  deps: QuotationRouterDeps,
  *,
  quotation_id: str,
  quote_no: str,
  customer_id: str,
  customer_name: str,
  contact_person: str,
  discount_rate: float,
  validity_days: int,
  validity_end_date: str,
  quote_status: int,
  remark: str,
  items: list[dict[str, Any]],
) -> bool:
  if not quote_no or not customer_name:
    raise QuotationServiceError('报价单号和客户名称不能为空', 400)
  if not items:
    raise QuotationServiceError('报价明细不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  old_row = fetch_quotation_edit_guard_row(cur, quotation_id)
  if not old_row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  if deps.safe_int_func(old_row['status'], 0) in (2, 4, 5):
    conn.close()
    raise QuotationServiceError('当前状态不允许编辑', 400)

  try:
    total_amount = save_quotation_items(cur, quotation_id, items, deps.safe_float_func, deps.safe_int_func)
    final_amount = round(total_amount * discount_rate / 100, 2)
    update_quotation_row(
      cur,
      quotation_id=quotation_id,
      quote_no=quote_no,
      customer_id=customer_id,
      customer_name=customer_name,
      contact_person=contact_person,
      total_amount=total_amount,
      discount_rate=discount_rate,
      final_amount=final_amount,
      validity_days=validity_days,
      validity_end_date=validity_end_date,
      status=quote_status,
      remark=remark,
      now=deps.now_str_func(),
    )
    conn.commit()
  except DatabaseIntegrityError as error:
    conn.rollback()
    conn.close()
    raise QuotationServiceError('报价单号已存在', 400) from error
  except Exception as error:
    conn.rollback()
    conn.close()
    print('更新报价单失败:', error)
    raise QuotationServiceError('更新报价单失败', 500) from error

  conn.close()
  return True


def delete_quotation(deps: QuotationRouterDeps, *, quotation_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_quotation_status_row(cur, quotation_id)
  if not row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  if deps.safe_int_func(row['status'], 0) != 0:
    conn.close()
    raise QuotationServiceError('仅草稿状态可删除', 400)

  delete_quotation_items(cur, quotation_id)
  delete_quotation_approval_logs(cur, quotation_id)
  delete_quotation_row(cur, quotation_id)
  conn.commit()
  conn.close()
  return True


def submit_quotation(deps: QuotationRouterDeps, *, quotation_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_quotation_submit_row(cur, quotation_id)
  if not row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  if deps.safe_int_func(row['status'], 0) != 0:
    conn.close()
    raise QuotationServiceError('仅草稿状态可提交审批', 400)

  flow_id, nodes = resolve_quotation_approval_flow(cur, deps.safe_int_func)
  if flow_id <= 0:
    conn.close()
    raise QuotationServiceError('未配置启用的报价审批规则，请先在审批规则中配置 approval_type=4', 400)
  if not nodes:
    conn.close()
    raise QuotationServiceError('报价审批规则未配置节点', 400)

  first_node_index = deps.safe_int_func(nodes[0]['node_index'], 1)
  delete_quotation_approval_logs(cur, quotation_id)
  update_quotation_submit_state(
    cur,
    quotation_id=quotation_id,
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
      title='报价单待审批',
      content=f'报价单 {quotation_id} 已提交审批，请尽快处理',
      ntype=1,
      biz_type='quotation',
      biz_id=quotation_id,
    )
  return True


def approve_quotation(
  deps: QuotationRouterDeps,
  *,
  quotation_id: str,
  user_id: str,
  user_name: str,
) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_quotation_approval_row(cur, quotation_id)
  if not row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  if deps.safe_int_func(row['status'], 0) != 1:
    conn.close()
    raise QuotationServiceError('仅待审批状态可通过', 400)

  flow_id = deps.safe_int_func(row['approval_flow_id'], 0)
  current_node_index = deps.safe_int_func(row['current_node_index'], 0)
  if flow_id <= 0 or current_node_index <= 0:
    conn.close()
    raise QuotationServiceError('审批流程异常，请重新提交该报价单', 400)

  node = fetch_approval_node(cur, flow_id, current_node_index)
  if not node:
    conn.close()
    raise QuotationServiceError('未找到当前审批节点，请检查审批规则配置', 400)
  if not is_user_allowed_for_node(cur, node, user_id):
    conn.close()
    raise QuotationServiceError('当前用户不在本节点审批人范围内', 403)

  now = deps.now_str_func()
  insert_quotation_approval_log(
    cur,
    approval_log_id=str(uuid.uuid4()),
    quotation_id=quotation_id,
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
    raise QuotationServiceError('审批节点顺序异常，请检查审批规则配置', 400)

  if current_pos >= len(node_indexes) - 1:
    update_quotation_approved(cur, quotation_id=quotation_id, now=now)
  else:
    next_node_index = node_indexes[current_pos + 1]
    update_quotation_current_node(cur, quotation_id=quotation_id, current_node_index=next_node_index, now=now)

  conn.commit()
  conn.close()
  return True


def reject_quotation(
  deps: QuotationRouterDeps,
  *,
  quotation_id: str,
  user_id: str,
  user_name: str,
  remark: str,
) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_quotation_approval_row(cur, quotation_id)
  if not row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  if deps.safe_int_func(row['status'], 0) != 1:
    conn.close()
    raise QuotationServiceError('仅待审批状态可驳回', 400)

  flow_id = deps.safe_int_func(row['approval_flow_id'], 0)
  current_node_index = deps.safe_int_func(row['current_node_index'], 0)
  node = fetch_approval_node(cur, flow_id, current_node_index)
  if not node:
    conn.close()
    raise QuotationServiceError('未找到当前审批节点', 400)
  if not is_user_allowed_for_node(cur, node, user_id):
    conn.close()
    raise QuotationServiceError('当前用户不在本节点审批人范围内', 403)

  now = deps.now_str_func()
  insert_quotation_approval_log(
    cur,
    approval_log_id=str(uuid.uuid4()),
    quotation_id=quotation_id,
    approval_flow_id=flow_id,
    node_index=current_node_index,
    node_name=node['approval_node_name'] or '',
    approver_id=user_id,
    approver_name=user_name,
    action='reject',
    remark=remark,
    action_time=now,
  )
  update_quotation_rejected(cur, quotation_id=quotation_id, now=now)
  conn.commit()
  conn.close()
  return True


def cancel_quotation(deps: QuotationRouterDeps, *, quotation_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_quotation_status_row(cur, quotation_id)
  if not row:
    conn.close()
    raise QuotationServiceError('报价单不存在', 404)
  if deps.safe_int_func(row['status'], 0) not in (0, 1, 3):
    conn.close()
    raise QuotationServiceError('仅草稿/待审批/已驳回状态可作废', 400)

  update_quotation_cancelled(cur, quotation_id=quotation_id, now=deps.now_str_func())
  conn.commit()
  conn.close()
  return True
