from __future__ import annotations

from typing import Any


def query_device_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM devices {where_sql}', values)
  return cur.fetchone()


def query_device_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, device_name, device_number, model, device_category_id, workstation_id,
           responsible_person, status, remarks, scrap_reason, create_time, update_time
    FROM devices
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_device_list_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT id, device_name, device_number, model, device_category_id, workstation_id,
           responsible_person, status, remarks, scrap_reason, create_time, update_time
    FROM devices
    ORDER BY device_number ASC
    ''',
  )
  return cur.fetchall()


def fetch_device_detail_row(cur: Any, device_id: str) -> Any:
  cur.execute(
    '''
    SELECT id, device_name, device_number, model, device_category_id, workstation_id,
           responsible_person, status, remarks, scrap_reason, create_time, update_time
    FROM devices
    WHERE id = ?
    ''',
    (device_id,),
  )
  return cur.fetchone()


def query_device_category_rows(cur: Any) -> list[Any]:
  cur.execute('SELECT id, name FROM basic_infos WHERE type = 13')
  return cur.fetchall()


def fetch_device_by_number(cur: Any, device_number: str) -> Any:
  cur.execute('SELECT id FROM devices WHERE device_number = ?', (device_number,))
  return cur.fetchone()


def fetch_device_by_id(cur: Any, device_id: str) -> Any:
  cur.execute('SELECT id FROM devices WHERE id = ?', (device_id,))
  return cur.fetchone()


def fetch_other_device_by_number(cur: Any, device_number: str, device_id: str) -> Any:
  cur.execute('SELECT id FROM devices WHERE device_number = ? AND id <> ?', (device_number, device_id))
  return cur.fetchone()


def insert_device(
  cur: Any,
  *,
  device_id: str,
  device_name: str,
  device_number: str,
  model: str,
  device_category_id: str,
  workstation_id: str,
  responsible_person: str,
  status: int,
  remarks: str,
  scrap_reason: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO devices(
      id, device_name, device_number, model, device_category_id, workstation_id,
      responsible_person, status, remarks, scrap_reason, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      device_id,
      device_name,
      device_number,
      model,
      device_category_id,
      workstation_id,
      responsible_person,
      status,
      remarks,
      scrap_reason,
      now,
      now,
    ),
  )


def update_device(
  cur: Any,
  *,
  device_id: str,
  device_name: str,
  device_number: str,
  model: str,
  device_category_id: str,
  workstation_id: str,
  responsible_person: str,
  status: int,
  remarks: str,
  scrap_reason: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE devices
    SET device_name = ?, device_number = ?, model = ?, device_category_id = ?, workstation_id = ?,
        responsible_person = ?, status = ?, remarks = ?, scrap_reason = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      device_name,
      device_number,
      model,
      device_category_id,
      workstation_id,
      responsible_person,
      status,
      remarks,
      scrap_reason,
      now,
      device_id,
    ),
  )


def delete_device(cur: Any, device_id: str) -> None:
  cur.execute('DELETE FROM devices WHERE id = ?', (device_id,))


def update_device_status(cur: Any, *, device_id: str, status: int, scrap_reason: str, now: str) -> None:
  cur.execute(
    'UPDATE devices SET status = ?, scrap_reason = ?, update_time = ? WHERE id = ?',
    (status, scrap_reason, now, device_id),
  )
