from __future__ import annotations

from app.modules.approval_flow.deps import ApprovalFlowRouterDeps
from app.modules.approval_flow.repositories.approval_flow_result_repo import (
  fetch_approval_result_by_id,
  insert_approval_result,
  update_approval_result,
)
from app.modules.approval_flow.services.errors import ApprovalFlowServiceError


def save_approval_result(
  deps: ApprovalFlowRouterDeps,
  *,
  record_id: int,
  order_id: str,
  order_scheduling_id: str,
  order_name: str,
  product_name: str,
  process_library_id: str,
  approval_flow_id: int,
  process_people: str,
  approval_status: int,
  approval_remarks: str,
) -> bool:
  if not order_scheduling_id:
    raise ApprovalFlowServiceError('orderSchedulingId不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  now = deps.now_str_func()
  if record_id > 0 and fetch_approval_result_by_id(cur, record_id):
    update_approval_result(
      cur,
      record_id=record_id,
      order_id=order_id,
      order_scheduling_id=order_scheduling_id,
      order_name=order_name,
      product_name=product_name,
      process_library_id=process_library_id,
      approval_flow_id=approval_flow_id if approval_flow_id > 0 else None,
      process_people=process_people,
      approval_status=approval_status,
      approval_remarks=approval_remarks,
      now=now,
    )
    conn.commit()
    conn.close()
    return True

  insert_approval_result(
    cur,
    order_id=order_id,
    order_scheduling_id=order_scheduling_id,
    order_name=order_name,
    product_name=product_name,
    process_library_id=process_library_id,
    approval_flow_id=approval_flow_id if approval_flow_id > 0 else None,
    process_people=process_people,
    approval_status=approval_status,
    approval_remarks=approval_remarks,
    now=now,
  )
  conn.commit()
  conn.close()
  return True
