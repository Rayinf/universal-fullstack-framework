from __future__ import annotations

from typing import Any

from app.bootstrap.init_db_schema_shared import table_columns


def _ensure_purchase_order_columns(cur: Any) -> None:
  purchase_columns = table_columns(cur, 'purchase_orders')
  if 'approval_flow_id' not in purchase_columns:
    cur.execute('ALTER TABLE purchase_orders ADD COLUMN approval_flow_id INTEGER')
  if 'current_node_index' not in purchase_columns:
    cur.execute('ALTER TABLE purchase_orders ADD COLUMN current_node_index INTEGER NOT NULL DEFAULT 0')


def apply_sales_schema(cur: Any) -> None:
  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS purchase_orders (
      id TEXT PRIMARY KEY,
      order_no TEXT NOT NULL UNIQUE,
      supplier_name TEXT NOT NULL,
      item_name TEXT NOT NULL,
      quantity REAL NOT NULL DEFAULT 0,
      unit_price REAL NOT NULL DEFAULT 0,
      total_amount REAL NOT NULL DEFAULT 0,
      status INTEGER NOT NULL DEFAULT 0,
      applicant TEXT,
      remark TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )
  _ensure_purchase_order_columns(cur)

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS purchase_order_approval_logs (
      id TEXT PRIMARY KEY,
      order_id TEXT NOT NULL,
      approval_flow_id INTEGER,
      node_index INTEGER NOT NULL,
      node_name TEXT NOT NULL,
      approver_id TEXT,
      approver_name TEXT,
      action TEXT NOT NULL,
      remark TEXT,
      action_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS quotations (
      id TEXT PRIMARY KEY,
      quote_no TEXT NOT NULL UNIQUE,
      customer_id TEXT,
      customer_name TEXT NOT NULL,
      contact_person TEXT,
      total_amount REAL NOT NULL DEFAULT 0,
      discount_rate REAL NOT NULL DEFAULT 100,
      final_amount REAL NOT NULL DEFAULT 0,
      validity_days INTEGER NOT NULL DEFAULT 30,
      validity_end_date TEXT,
      status INTEGER NOT NULL DEFAULT 0,
      applicant TEXT,
      approval_flow_id INTEGER,
      current_node_index INTEGER NOT NULL DEFAULT 0,
      version INTEGER NOT NULL DEFAULT 1,
      remark TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS quotation_items (
      id TEXT PRIMARY KEY,
      quotation_id TEXT NOT NULL,
      product_id TEXT,
      product_code TEXT,
      product_name TEXT NOT NULL,
      specification TEXT,
      unit TEXT NOT NULL DEFAULT 'pcs',
      quantity REAL NOT NULL DEFAULT 0,
      unit_price REAL NOT NULL DEFAULT 0,
      amount REAL NOT NULL DEFAULT 0,
      sort_order INTEGER NOT NULL DEFAULT 0,
      remark TEXT
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS quotation_approval_logs (
      id TEXT PRIMARY KEY,
      quotation_id TEXT NOT NULL,
      approval_flow_id INTEGER,
      node_index INTEGER NOT NULL,
      node_name TEXT NOT NULL,
      approver_id TEXT,
      approver_name TEXT,
      action TEXT NOT NULL,
      remark TEXT,
      action_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS contracts (
      id TEXT PRIMARY KEY,
      contract_no TEXT NOT NULL UNIQUE,
      quotation_id TEXT,
      customer_id TEXT,
      customer_name TEXT NOT NULL,
      contract_name TEXT NOT NULL,
      total_amount REAL NOT NULL DEFAULT 0,
      paid_amount REAL NOT NULL DEFAULT 0,
      signed_date TEXT,
      start_date TEXT,
      end_date TEXT,
      payment_terms TEXT,
      status INTEGER NOT NULL DEFAULT 0,
      expire_warning_sent INTEGER NOT NULL DEFAULT 0,
      remark TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS payment_records (
      id TEXT PRIMARY KEY,
      contract_id TEXT NOT NULL,
      payment_no TEXT NOT NULL UNIQUE,
      payment_amount REAL NOT NULL DEFAULT 0,
      payment_date TEXT,
      payment_method INTEGER NOT NULL DEFAULT 1,
      payer_name TEXT,
      received_by TEXT,
      remark TEXT,
      status INTEGER NOT NULL DEFAULT 0,
      create_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS commission_records (
      id TEXT PRIMARY KEY,
      contract_id TEXT NOT NULL,
      contract_no TEXT,
      customer_name TEXT,
      salesperson_id TEXT,
      salesperson_name TEXT,
      contract_amount REAL NOT NULL DEFAULT 0,
      payment_amount REAL NOT NULL DEFAULT 0,
      commission_rate REAL NOT NULL DEFAULT 0,
      commission_amount REAL NOT NULL DEFAULT 0,
      status INTEGER NOT NULL DEFAULT 0,
      pay_date TEXT,
      remark TEXT,
      create_time TEXT NOT NULL
    )
    ''',
  )
