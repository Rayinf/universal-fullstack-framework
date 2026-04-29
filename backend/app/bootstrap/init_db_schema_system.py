from __future__ import annotations

from typing import Any

from app.bootstrap.init_db_schema_shared import table_columns


def _ensure_role_columns(cur: Any) -> None:
  role_columns = table_columns(cur, 'roles')
  if 'role_code' not in role_columns:
    cur.execute("ALTER TABLE roles ADD COLUMN role_code TEXT DEFAULT ''")
  if 'role_desc' not in role_columns:
    cur.execute("ALTER TABLE roles ADD COLUMN role_desc TEXT DEFAULT ''")
  if 'create_time' not in role_columns:
    cur.execute("ALTER TABLE roles ADD COLUMN create_time TEXT DEFAULT ''")
  if 'update_time' not in role_columns:
    cur.execute("ALTER TABLE roles ADD COLUMN update_time TEXT DEFAULT ''")


def apply_system_schema(cur: Any) -> None:
  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS roles (
      role_id TEXT PRIMARY KEY,
      role_name TEXT NOT NULL,
      del_flag TEXT DEFAULT '0'
    )
    ''',
  )
  _ensure_role_columns(cur)

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS users (
      user_id TEXT PRIMARY KEY,
      username TEXT NOT NULL UNIQUE,
      password TEXT NOT NULL,
      real_name TEXT NOT NULL,
      phone TEXT,
      email TEXT,
      enabled INTEGER DEFAULT 0,
      role_id TEXT DEFAULT '2',
      dept_id TEXT DEFAULT '1',
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL,
      FOREIGN KEY(role_id) REFERENCES roles(role_id)
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS system_config (
      id INTEGER PRIMARY KEY,
      company_name TEXT NOT NULL,
      system_name TEXT NOT NULL,
      version TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS depts (
      dept_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      parent_id TEXT NOT NULL DEFAULT '0',
      sort_order INTEGER DEFAULT 0,
      enabled INTEGER DEFAULT 0,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS role_menus (
      role_id TEXT NOT NULL,
      menu_id TEXT NOT NULL,
      PRIMARY KEY (role_id, menu_id)
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS sys_log_users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      type INTEGER NOT NULL DEFAULT 1,
      content TEXT NOT NULL,
      sys_log_id TEXT,
      creator TEXT,
      create_by TEXT,
      real_name TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL,
      tenant_code TEXT DEFAULT 'LOCAL'
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS sys_backup_infos (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      type INTEGER NOT NULL DEFAULT 1,
      status INTEGER NOT NULL DEFAULT 1,
      file_content TEXT NOT NULL,
      create_name TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS sys_backup_configs (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      enabled INTEGER NOT NULL DEFAULT 1,
      cron_expression TEXT NOT NULL,
      retention_days INTEGER NOT NULL DEFAULT 30,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS approval_flows (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      approval_flow_name TEXT NOT NULL,
      process_library_id TEXT,
      approval_type INTEGER NOT NULL,
      status INTEGER NOT NULL DEFAULT 1,
      remarks TEXT,
      creator TEXT,
      create_by TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL,
      is_deleted INTEGER NOT NULL DEFAULT 0
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS approval_flow_nodes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      approval_flow_id INTEGER NOT NULL,
      approval_node_name TEXT NOT NULL,
      role_id TEXT,
      approval_ids TEXT,
      node_index INTEGER NOT NULL DEFAULT 1,
      remarks TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS approval_flow_results (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id TEXT,
      result_type INTEGER NOT NULL DEFAULT 1,
      order_scheduling_id TEXT,
      order_name TEXT,
      product_name TEXT,
      process_library_id TEXT,
      approval_flow_id INTEGER,
      process_people TEXT,
      approval_status INTEGER NOT NULL DEFAULT 3,
      approval_remarks TEXT,
      creator TEXT,
      create_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS notifications (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      title TEXT NOT NULL,
      content TEXT,
      type INTEGER NOT NULL DEFAULT 3,
      biz_type TEXT,
      biz_id TEXT,
      is_read INTEGER NOT NULL DEFAULT 0,
      create_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS attachments (
      id TEXT PRIMARY KEY,
      biz_type TEXT NOT NULL,
      biz_id TEXT NOT NULL,
      file_name TEXT NOT NULL,
      file_size INTEGER NOT NULL DEFAULT 0,
      file_path TEXT NOT NULL,
      upload_by TEXT,
      upload_time TEXT NOT NULL
    )
    ''',
  )
