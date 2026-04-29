from __future__ import annotations

from typing import Any


def query_project_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM projects {where_sql}', values)
  return cur.fetchone()


def query_project_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, project_code, project_name, owner_name, priority, status, progress,
           start_date, end_date, remark, create_time, update_time
    FROM projects
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def fetch_project_id(cur: Any, project_id: str) -> Any:
  cur.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
  return cur.fetchone()


def insert_project(
  cur: Any,
  *,
  project_id: str,
  project_code: str,
  project_name: str,
  owner_name: str,
  priority: int,
  project_status: int,
  progress: int,
  start_date: str,
  end_date: str,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO projects(
      id, project_code, project_name, owner_name, priority, status, progress,
      start_date, end_date, remark, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      project_id,
      project_code,
      project_name,
      owner_name,
      priority,
      project_status,
      progress,
      start_date,
      end_date,
      remark,
      now,
      now,
    ),
  )


def update_project(
  cur: Any,
  *,
  project_id: str,
  project_code: str,
  project_name: str,
  owner_name: str,
  priority: int,
  project_status: int,
  progress: int,
  start_date: str,
  end_date: str,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE projects
    SET project_code = ?, project_name = ?, owner_name = ?, priority = ?, status = ?, progress = ?,
        start_date = ?, end_date = ?, remark = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      project_code,
      project_name,
      owner_name,
      priority,
      project_status,
      progress,
      start_date,
      end_date,
      remark,
      now,
      project_id,
    ),
  )


def delete_project(cur: Any, project_id: str) -> None:
  cur.execute('DELETE FROM projects WHERE id = ?', (project_id,))
