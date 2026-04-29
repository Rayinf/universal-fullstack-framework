from __future__ import annotations

from typing import Any

from app.bootstrap.init_db_schema_shared import table_columns


def _ensure_inventory_transaction_columns(cur: Any) -> None:
  inventory_tx_columns = table_columns(cur, 'inventory_transactions')
  if 'after_stock' not in inventory_tx_columns:
    cur.execute('ALTER TABLE inventory_transactions ADD COLUMN after_stock REAL NOT NULL DEFAULT 0')


def apply_demo_common_schema(cur: Any) -> None:
  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS crud_items (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      code TEXT NOT NULL UNIQUE,
      remark TEXT,
      status INTEGER DEFAULT 0,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS projects (
      id TEXT PRIMARY KEY,
      project_code TEXT NOT NULL UNIQUE,
      project_name TEXT NOT NULL,
      owner_name TEXT,
      priority INTEGER NOT NULL DEFAULT 2,
      status INTEGER NOT NULL DEFAULT 0,
      progress INTEGER NOT NULL DEFAULT 0,
      start_date TEXT,
      end_date TEXT,
      remark TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS inventory_items (
      id TEXT PRIMARY KEY,
      sku TEXT NOT NULL UNIQUE,
      item_name TEXT NOT NULL,
      unit TEXT NOT NULL DEFAULT 'pcs',
      stock_qty REAL NOT NULL DEFAULT 0,
      safety_qty REAL NOT NULL DEFAULT 0,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS inventory_transactions (
      id TEXT PRIMARY KEY,
      item_id TEXT NOT NULL,
      sku TEXT NOT NULL,
      item_name TEXT NOT NULL,
      direction INTEGER NOT NULL DEFAULT 1,
      quantity REAL NOT NULL DEFAULT 0,
      after_stock REAL NOT NULL DEFAULT 0,
      business_no TEXT,
      operator_name TEXT,
      remark TEXT,
      create_time TEXT NOT NULL
    )
    ''',
  )
  _ensure_inventory_transaction_columns(cur)

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS customers (
      id TEXT PRIMARY KEY,
      customer_code TEXT NOT NULL UNIQUE,
      customer_name TEXT NOT NULL,
      account_manager_name TEXT,
      introducer_name TEXT,
      customer_level INTEGER DEFAULT 3,
      special_notes TEXT,
      creator TEXT DEFAULT '系统管理员',
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS workstations (
      id TEXT PRIMARY KEY,
      workstation_no INTEGER NOT NULL UNIQUE,
      workstation_name TEXT NOT NULL,
      workstation_type INTEGER NOT NULL DEFAULT 1,
      status INTEGER NOT NULL DEFAULT 1,
      responsible_person TEXT,
      dept_id TEXT,
      process_library_id TEXT,
      remarks TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS devices (
      id TEXT PRIMARY KEY,
      device_name TEXT NOT NULL,
      device_number TEXT NOT NULL UNIQUE,
      model TEXT NOT NULL,
      device_category_id TEXT,
      workstation_id TEXT,
      responsible_person TEXT,
      status INTEGER NOT NULL DEFAULT 1,
      remarks TEXT,
      scrap_reason TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS basic_infos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      type INTEGER NOT NULL,
      parent_id INTEGER,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS scan_binding_processes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      scan_asset_number TEXT NOT NULL,
      identifier TEXT NOT NULL,
      process_id INTEGER NOT NULL,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS code_rules (
      id TEXT PRIMARY KEY,
      type INTEGER NOT NULL UNIQUE,
      prefix TEXT NOT NULL,
      rule_name TEXT NOT NULL,
      is_enable INTEGER NOT NULL DEFAULT 0,
      remark TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS product_catalog (
      id TEXT PRIMARY KEY,
      product_code TEXT NOT NULL UNIQUE,
      product_name TEXT NOT NULL,
      specification TEXT,
      unit TEXT NOT NULL DEFAULT 'pcs',
      reference_price REAL NOT NULL DEFAULT 0,
      cost_price REAL NOT NULL DEFAULT 0,
      category TEXT,
      status INTEGER NOT NULL DEFAULT 1,
      remark TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )
