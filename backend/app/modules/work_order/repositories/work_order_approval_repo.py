from __future__ import annotations

from typing import Any


def fetch_enabled_approval_flow(cur: Any, approval_type: int) -> Any:
  cur.execute(
    '''
    SELECT id
    FROM approval_flows
    WHERE is_deleted = 0 AND status = 1 AND approval_type = ?
    ORDER BY update_time DESC, id DESC
    LIMIT 1
    ''',
    (approval_type,),
  )
  return cur.fetchone()


def fetch_approval_flow_nodes(cur: Any, approval_flow_id: int) -> list[Any]:
  cur.execute(
    '''
    SELECT id, approval_node_name, role_id, approval_ids, node_index
    FROM approval_flow_nodes
    WHERE approval_flow_id = ?
    ORDER BY node_index ASC, id ASC
    ''',
    (approval_flow_id,),
  )
  return cur.fetchall()


def fetch_approval_node(cur: Any, approval_flow_id: int, node_index: int) -> Any:
  cur.execute(
    '''
    SELECT id, approval_node_name, role_id, approval_ids, node_index
    FROM approval_flow_nodes
    WHERE approval_flow_id = ? AND node_index = ?
    LIMIT 1
    ''',
    (approval_flow_id, node_index),
  )
  return cur.fetchone()


def fetch_work_order_approval_logs(cur: Any, work_order_id: str) -> list[Any]:
  cur.execute(
    '''
    SELECT node_index, approver_id, approver_name, action, action_time
    FROM work_order_approval_logs
    WHERE work_order_id = ?
    ORDER BY node_index ASC, action_time ASC
    ''',
    (work_order_id,),
  )
  return cur.fetchall()


def delete_work_order_approval_logs(cur: Any, work_order_id: str) -> None:
  cur.execute('DELETE FROM work_order_approval_logs WHERE work_order_id = ?', (work_order_id,))


def insert_work_order_approval_log(
  cur: Any,
  *,
  approval_log_id: str,
  work_order_id: str,
  approval_flow_id: int,
  node_index: int,
  node_name: str,
  approver_id: str,
  approver_name: str,
  action: str,
  remark: str,
  action_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO work_order_approval_logs(
      id, work_order_id, approval_flow_id, node_index, node_name,
      approver_id, approver_name, action, remark, action_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      approval_log_id,
      work_order_id,
      approval_flow_id,
      node_index,
      node_name,
      approver_id,
      approver_name,
      action,
      remark,
      action_time,
    ),
  )
