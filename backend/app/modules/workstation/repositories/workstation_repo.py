from __future__ import annotations

from typing import Any


def query_workstation_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM workstations {where_sql}', values)
  return cur.fetchone()


def query_workstation_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, workstation_no, workstation_name, workstation_type, status,
           responsible_person, dept_id, process_library_id, remarks, create_time, update_time
    FROM workstations
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_workstation_list_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT id, workstation_no, workstation_name, workstation_type, status,
           responsible_person, dept_id, process_library_id, remarks, create_time, update_time
    FROM workstations
    ORDER BY workstation_no ASC
    ''',
  )
  return cur.fetchall()


def fetch_workstation_detail_row(cur: Any, workstation_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, workstation_no, workstation_name, workstation_type, status,
           responsible_person, dept_id, process_library_id, remarks, create_time, update_time
    FROM workstations
    WHERE id = ?
    ''',
    (workstation_id,),
  )
  return cur.fetchone()


def fetch_workstation_by_id(cur: Any, workstation_id: str) -> Any:
  cur.execute('SELECT id FROM workstations WHERE id = ?', (workstation_id,))
  return cur.fetchone()


def fetch_workstation_by_no(cur: Any, workstation_no: int) -> Any:
  cur.execute('SELECT id FROM workstations WHERE workstation_no = ?', (workstation_no,))
  return cur.fetchone()


def fetch_other_workstation_by_no(cur: Any, workstation_no: int, workstation_id: str) -> Any:
  cur.execute('SELECT id FROM workstations WHERE workstation_no = ? AND id <> ?', (workstation_no, workstation_id))
  return cur.fetchone()


def insert_workstation(
  cur: Any,
  *,
  workstation_id: str,
  workstation_no: int,
  workstation_name: str,
  workstation_type: int,
  status: int,
  responsible_person: str,
  dept_id: str,
  process_library_id: str,
  remarks: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO workstations(
      id, workstation_no, workstation_name, workstation_type, status,
      responsible_person, dept_id, process_library_id, remarks, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      workstation_id,
      workstation_no,
      workstation_name,
      workstation_type,
      status,
      responsible_person,
      dept_id,
      process_library_id,
      remarks,
      now,
      now,
    ),
  )


def update_workstation(
  cur: Any,
  *,
  workstation_id: str,
  workstation_no: int,
  workstation_name: str,
  workstation_type: int,
  status: int,
  responsible_person: str,
  dept_id: str,
  process_library_id: str,
  remarks: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE workstations
    SET workstation_no = ?, workstation_name = ?, workstation_type = ?, status = ?,
        responsible_person = ?, dept_id = ?, process_library_id = ?, remarks = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      workstation_no,
      workstation_name,
      workstation_type,
      status,
      responsible_person,
      dept_id,
      process_library_id,
      remarks,
      now,
      workstation_id,
    ),
  )


def delete_devices_by_workstation(cur: Any, workstation_id: str) -> None:
  cur.execute('DELETE FROM devices WHERE workstation_id = ?', (workstation_id,))


def delete_workstation(cur: Any, workstation_id: str) -> None:
  cur.execute('DELETE FROM workstations WHERE id = ?', (workstation_id,))


def update_workstation_status(cur: Any, workstation_id: str, status: int, now: str) -> None:
  cur.execute(
    'UPDATE workstations SET status = ?, update_time = ? WHERE id = ?',
    (status, now, workstation_id),
  )
