from __future__ import annotations

from typing import Any


def query_sys_backup_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM sys_backup_infos {where_sql}', values)
  return cur.fetchone()


def query_sys_backup_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, name, type, status, create_name, create_time
    FROM sys_backup_infos
    {where_sql}
    ORDER BY create_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def insert_sys_backup_info(
  cur: Any,
  *,
  backup_id: str,
  file_name: str,
  file_content: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO sys_backup_infos(id, name, type, status, file_content, create_name, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (backup_id, file_name, 1, 1, file_content, '系统管理员', now, now),
  )


def delete_sys_backup_info(cur: Any, backup_id: str) -> None:
  cur.execute('DELETE FROM sys_backup_infos WHERE id = ?', (backup_id,))


def delete_sys_backup_config(cur: Any, backup_id: str) -> None:
  cur.execute('DELETE FROM sys_backup_configs WHERE id = ?', (backup_id,))


def fetch_sys_backup_download(cur: Any, backup_id: str) -> Any:
  cur.execute('SELECT name, file_content FROM sys_backup_infos WHERE id = ?', (backup_id,))
  return cur.fetchone()


def fetch_latest_sys_backup_config(cur: Any) -> Any:
  cur.execute(
    '''
    SELECT id, name, enabled, cron_expression, retention_days, create_time, update_time
    FROM sys_backup_configs
    ORDER BY update_time DESC
    LIMIT 1
    ''',
    (),
  )
  return cur.fetchone()


def fetch_sys_backup_config_id(cur: Any, plan_id: str) -> Any:
  cur.execute('SELECT id FROM sys_backup_configs WHERE id = ?', (plan_id,))
  return cur.fetchone()


def update_sys_backup_config(
  cur: Any,
  *,
  plan_id: str,
  name: str,
  enabled: int,
  cron_expression: str,
  retention_days: int,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE sys_backup_configs
    SET name = ?, enabled = ?, cron_expression = ?, retention_days = ?, update_time = ?
    WHERE id = ?
    ''',
    (name, enabled, cron_expression, retention_days, now, plan_id),
  )


def insert_sys_backup_config(
  cur: Any,
  *,
  plan_id: str,
  name: str,
  enabled: int,
  cron_expression: str,
  retention_days: int,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO sys_backup_configs(
      id, name, enabled, cron_expression, retention_days, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',
    (plan_id, name, enabled, cron_expression, retention_days, now, now),
  )
