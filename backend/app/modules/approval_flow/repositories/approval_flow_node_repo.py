from __future__ import annotations

from typing import Any


def fetch_approval_flow_nodes(cur: Any, flow_id: int) -> list[Any]:
  cur.execute(
    '''
    SELECT id, approval_node_name, role_id, approval_ids, node_index, remarks
    FROM approval_flow_nodes
    WHERE approval_flow_id = ?
    ORDER BY node_index ASC, id ASC
    ''',
    (flow_id,),
  )
  return cur.fetchall()


def delete_approval_flow_nodes(cur: Any, flow_id: int) -> None:
  cur.execute('DELETE FROM approval_flow_nodes WHERE approval_flow_id = ?', (flow_id,))


def insert_approval_flow_node(
  cur: Any,
  *,
  flow_id: int,
  approval_node_name: str,
  role_id: str,
  approval_ids: str,
  node_index: int,
  remarks: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO approval_flow_nodes(
      approval_flow_id, approval_node_name, role_id, approval_ids, node_index, remarks, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (flow_id, approval_node_name, role_id, approval_ids, node_index, remarks, now, now),
  )
