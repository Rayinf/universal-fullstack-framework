from __future__ import annotations

from typing import Any


def query_approval_flow_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM approval_flows {where_sql}', values)
  return cur.fetchone()


def query_approval_flow_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, approval_flow_name, process_library_id, approval_type, status, remarks, creator, create_by, create_time, update_time
    FROM approval_flows
    {where_sql}
    ORDER BY update_time DESC, id DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_approval_flow_list_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT id, approval_flow_name, process_library_id, approval_type, status, remarks, creator, create_by, create_time, update_time
    FROM approval_flows
    WHERE is_deleted = 0
    ORDER BY update_time DESC, id DESC
    ''',
  )
  return cur.fetchall()


def fetch_approval_flow_detail_row(cur: Any, flow_id: int) -> Any:
  cur.execute(
    '''
    SELECT id, approval_flow_name, process_library_id, approval_type, status, remarks
    FROM approval_flows
    WHERE id = ? AND is_deleted = 0
    ''',
    (flow_id,),
  )
  return cur.fetchone()


def fetch_approval_flow_by_name(cur: Any, approval_flow_name: str) -> Any:
  cur.execute('SELECT id FROM approval_flows WHERE is_deleted = 0 AND approval_flow_name = ?', (approval_flow_name,))
  return cur.fetchone()


def fetch_approval_flow_by_id(cur: Any, flow_id: int) -> Any:
  cur.execute('SELECT id FROM approval_flows WHERE id = ? AND is_deleted = 0', (flow_id,))
  return cur.fetchone()


def fetch_other_approval_flow_by_name(cur: Any, flow_id: int, approval_flow_name: str) -> Any:
  cur.execute(
    'SELECT id FROM approval_flows WHERE id <> ? AND is_deleted = 0 AND approval_flow_name = ?',
    (flow_id, approval_flow_name),
  )
  return cur.fetchone()


def insert_approval_flow(
  cur: Any,
  *,
  approval_flow_name: str,
  process_library_id: str,
  approval_type: int,
  status: int,
  remarks: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO approval_flows(
      approval_flow_name, process_library_id, approval_type, status, remarks,
      creator, create_by, create_time, update_time, is_deleted
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''',
    (approval_flow_name, process_library_id, approval_type, status, remarks, '系统管理员', '1', now, now),
  )


def update_approval_flow(
  cur: Any,
  *,
  flow_id: int,
  approval_flow_name: str,
  process_library_id: str,
  approval_type: int,
  status: int,
  remarks: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE approval_flows
    SET approval_flow_name = ?, process_library_id = ?, approval_type = ?, status = ?, remarks = ?, update_time = ?
    WHERE id = ?
    ''',
    (approval_flow_name, process_library_id, approval_type, status, remarks, now, flow_id),
  )


def soft_delete_approval_flow(cur: Any, flow_id: int, now: str) -> None:
  cur.execute('UPDATE approval_flows SET is_deleted = 1, update_time = ? WHERE id = ?', (now, flow_id))


def query_approval_flow_name_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT id, approval_flow_name FROM approval_flows WHERE is_deleted = 0')
  return cur.fetchall()
