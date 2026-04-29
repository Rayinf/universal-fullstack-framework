from __future__ import annotations

import uuid

from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.helpers import resolve_work_order_notify_users
from app.modules.work_order.repositories.work_order_repo import (
  fetch_work_order_for_report,
  update_work_order_report_metrics,
)
from app.modules.work_order.repositories.work_report_repo import insert_work_report
from app.modules.work_order.services.errors import WorkOrderServiceError


def create_work_report(
  deps: WorkOrderRouterDeps,
  *,
  work_order_id: str,
  process_name: str,
  report_quantity: float,
  qualified_quantity: float,
  defect_quantity: float,
  report_user_id: str,
  report_user_name: str,
  report_time: str,
  remark: str,
) -> bool:
  if not work_order_id:
    raise WorkOrderServiceError('请选择生产工单', 400)
  if not process_name:
    raise WorkOrderServiceError('工序名称不能为空', 400)
  if report_quantity <= 0:
    raise WorkOrderServiceError('报工数量必须大于0', 400)
  if qualified_quantity < 0 or defect_quantity < 0:
    raise WorkOrderServiceError('合格/不良数量不能小于0', 400)
  if abs((qualified_quantity + defect_quantity) - report_quantity) > 0.0001:
    raise WorkOrderServiceError('合格数量 + 不良数量 必须等于报工数量', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  work_order = fetch_work_order_for_report(cur, work_order_id)
  if not work_order:
    conn.close()
    raise WorkOrderServiceError('生产工单不存在', 404)
  work_order_status = deps.safe_int_func(work_order['status'], 0)
  if work_order_status not in (2, 3, 4):
    conn.close()
    raise WorkOrderServiceError('当前工单状态不允许报工', 400)

  now = deps.now_str_func()
  old_qualified = deps.safe_float_func(work_order['qualified_quantity'], 0)
  new_qualified = old_qualified + qualified_quantity
  plan_quantity = deps.safe_float_func(work_order['plan_quantity'], 0)
  next_status = 3 if work_order_status in (2, 3) else work_order_status
  actual_start_time = now if work_order_status == 2 else None
  actual_end_time = None
  should_notify_inbound = False
  if plan_quantity > 0 and new_qualified >= plan_quantity:
    next_status = 4
    actual_end_time = now
    should_notify_inbound = work_order_status in (2, 3)

  notify_user_ids: list[str] = []
  work_order_no = str(work_order['work_order_no'] or work_order_id)
  try:
    insert_work_report(
      cur,
      report_id=str(uuid.uuid4()),
      work_order_id=work_order_id,
      work_order_no=str(work_order['work_order_no']),
      process_name=process_name,
      report_quantity=report_quantity,
      qualified_quantity=qualified_quantity,
      defect_quantity=defect_quantity,
      report_user_id=report_user_id,
      report_user_name=report_user_name,
      report_time=report_time,
      remark=remark,
      create_time=now,
    )
    update_work_order_report_metrics(
      cur,
      work_order_id=work_order_id,
      report_quantity=report_quantity,
      qualified_quantity=qualified_quantity,
      status=next_status,
      now=now,
      actual_start_time=actual_start_time,
      actual_end_time=actual_end_time,
    )

    if should_notify_inbound:
      notify_user_ids = resolve_work_order_notify_users(cur, str(work_order['applicant'] or ''))

    conn.commit()
  except Exception as error:
    conn.rollback()
    conn.close()
    print('新增工序报工失败:', error)
    raise WorkOrderServiceError('新增工序报工失败', 500) from error

  conn.close()
  if notify_user_ids:
    deps.create_notification_for_users_func(
      notify_user_ids,
      title='生产工单待入库',
      content=f'生产工单 {work_order_no} 已达到待入库状态，请尽快入库',
      ntype=1,
      biz_type='work_order',
      biz_id=work_order_id,
    )
  return True
