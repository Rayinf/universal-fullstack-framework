from __future__ import annotations

from typing import Any


def apply_production_schema(cur: Any) -> None:
  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS work_orders (
      id TEXT PRIMARY KEY,
      work_order_no TEXT NOT NULL UNIQUE,
      contract_id TEXT,
      contract_no TEXT,
      customer_name TEXT,
      product_id TEXT,
      product_code TEXT,
      product_name TEXT NOT NULL,
      plan_quantity REAL NOT NULL DEFAULT 0,
      reported_quantity REAL NOT NULL DEFAULT 0,
      qualified_quantity REAL NOT NULL DEFAULT 0,
      inbound_quantity REAL NOT NULL DEFAULT 0,
      status INTEGER NOT NULL DEFAULT 0,
      priority INTEGER NOT NULL DEFAULT 2,
      planned_start_date TEXT,
      planned_end_date TEXT,
      actual_start_time TEXT,
      actual_end_time TEXT,
      applicant TEXT,
      approval_flow_id INTEGER,
      current_node_index INTEGER NOT NULL DEFAULT 0,
      remark TEXT,
      create_time TEXT NOT NULL,
      update_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS work_order_approval_logs (
      id TEXT PRIMARY KEY,
      work_order_id TEXT NOT NULL,
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
    CREATE TABLE IF NOT EXISTS work_reports (
      id TEXT PRIMARY KEY,
      work_order_id TEXT NOT NULL,
      work_order_no TEXT NOT NULL,
      process_name TEXT NOT NULL,
      report_quantity REAL NOT NULL DEFAULT 0,
      qualified_quantity REAL NOT NULL DEFAULT 0,
      defect_quantity REAL NOT NULL DEFAULT 0,
      report_user_id TEXT,
      report_user_name TEXT,
      report_time TEXT NOT NULL,
      remark TEXT,
      create_time TEXT NOT NULL
    )
    ''',
  )

  cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS work_inbounds (
      id TEXT PRIMARY KEY,
      inbound_no TEXT NOT NULL UNIQUE,
      work_order_id TEXT NOT NULL,
      work_order_no TEXT NOT NULL,
      quantity REAL NOT NULL DEFAULT 0,
      warehouse_name TEXT,
      operator_name TEXT,
      inbound_time TEXT NOT NULL,
      remark TEXT,
      create_time TEXT NOT NULL
    )
    ''',
  )
