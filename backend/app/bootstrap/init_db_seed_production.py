from __future__ import annotations

from typing import Any, Callable


def seed_production_data(
  cur: Any,
  *,
  now_str: Callable[[], str],
  safe_int: Callable[[Any, int], int],
) -> None:
  t = now_str()

  cur.execute('SELECT COUNT(1) AS cnt FROM purchase_orders')
  purchase_cnt = int(cur.fetchone()['cnt'])
  if purchase_cnt == 0:
    purchase_seed = [
      (
        'po-1',
        'PO-20260302-001',
        '华北原料供应商',
        '轴承组件',
        120.0,
        36.5,
        4380.0,
        1,
        '系统管理员',
        '待财务复核',
        t,
        t,
      ),
      (
        'po-2',
        'PO-20260302-002',
        '华东电子供应商',
        '控制面板',
        40.0,
        210.0,
        8400.0,
        2,
        '系统管理员',
        '已审批通过',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO purchase_orders(
        id, order_no, supplier_name, item_name, quantity, unit_price, total_amount, status,
        applicant, remark, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      purchase_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM inventory_items')
  inventory_item_cnt = int(cur.fetchone()['cnt'])
  if inventory_item_cnt == 0:
    inventory_item_seed = [
      ('inv-1', 'SKU-1001', '轴承组件', 'pcs', 260.0, 80.0, t, t),
      ('inv-2', 'SKU-1002', '控制面板', 'pcs', 55.0, 30.0, t, t),
      ('inv-3', 'SKU-1003', '包装箱', 'pcs', 600.0, 120.0, t, t),
    ]
    cur.executemany(
      '''
      INSERT INTO inventory_items(
        id, sku, item_name, unit, stock_qty, safety_qty, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      inventory_item_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM inventory_transactions')
  inventory_tx_cnt = int(cur.fetchone()['cnt'])
  if inventory_tx_cnt == 0:
    inventory_tx_seed = [
      (
        'tx-1',
        'inv-1',
        'SKU-1001',
        '轴承组件',
        1,
        100.0,
        260.0,
        'PO-20260302-001',
        '系统管理员',
        '初始入库',
        t,
      ),
      (
        'tx-2',
        'inv-2',
        'SKU-1002',
        '控制面板',
        1,
        20.0,
        55.0,
        'PO-20260302-002',
        '系统管理员',
        '初始入库',
        t,
      ),
      (
        'tx-3',
        'inv-3',
        'SKU-1003',
        '包装箱',
        1,
        300.0,
        600.0,
        'INIT-001',
        '系统管理员',
        '初始入库',
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO inventory_transactions(
        id, item_id, sku, item_name, direction, quantity, after_stock, business_no, operator_name, remark, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      inventory_tx_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM approval_flows')
  approval_flow_cnt = int(cur.fetchone()['cnt'])
  default_tech_flow_id = 0
  if approval_flow_cnt == 0:
    cur.execute(
      '''
      INSERT INTO approval_flows(
        approval_flow_name, process_library_id, approval_type, status, remarks,
        creator, create_by, create_time, update_time, is_deleted
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
      ''',
      ('工艺库审批规则', '1', 1, 1, '本地默认审批规则', '系统管理员', '1', t, t),
    )
    cur.execute(
      '''
      SELECT id
      FROM approval_flows
      WHERE is_deleted = 0 AND approval_type = 1 AND approval_flow_name = ?
      ORDER BY id DESC
      LIMIT 1
      ''',
      ('工艺库审批规则',),
    )
    default_flow_row = cur.fetchone()
    default_tech_flow_id = safe_int(default_flow_row['id'] if default_flow_row else 0, 0)
    cur.execute(
      '''
      INSERT INTO approval_flow_nodes(
        approval_flow_id, approval_node_name, role_id, approval_ids, node_index, remarks, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      (default_tech_flow_id, '管理员审批', '1', '1', 1, '默认审批节点', t, t),
    )
  else:
    cur.execute(
      '''
      SELECT id
      FROM approval_flows
      WHERE is_deleted = 0 AND approval_type = 1
      ORDER BY id ASC
      LIMIT 1
      ''',
    )
    default_flow_row = cur.fetchone()
    default_tech_flow_id = safe_int(default_flow_row['id'] if default_flow_row else 0, 0)

  cur.execute('SELECT id FROM approval_flows WHERE is_deleted = 0 AND approval_type = 3 LIMIT 1')
  purchase_flow = cur.fetchone()
  if not purchase_flow:
    cur.execute(
      '''
      INSERT INTO approval_flows(
        approval_flow_name, process_library_id, approval_type, status, remarks,
        creator, create_by, create_time, update_time, is_deleted
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
      ''',
      ('采购订单审批规则', '', 3, 1, '采购业务默认审批规则', '系统管理员', '1', t, t),
    )
    cur.execute(
      '''
      SELECT id
      FROM approval_flows
      WHERE is_deleted = 0 AND approval_type = 3 AND approval_flow_name = ?
      ORDER BY id DESC
      LIMIT 1
      ''',
      ('采购订单审批规则',),
    )
    flow_row = cur.fetchone()
    flow_id = safe_int(flow_row['id'] if flow_row else 0, 0)
    cur.executemany(
      '''
      INSERT INTO approval_flow_nodes(
        approval_flow_id, approval_node_name, role_id, approval_ids, node_index, remarks, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      [
        (flow_id, '采购主管审批', '1', '1', 1, '默认节点1', t, t),
        (flow_id, '财务复核', '1', '1', 2, '默认节点2', t, t),
      ],
    )

  cur.execute('SELECT id FROM approval_flows WHERE is_deleted = 0 AND approval_type = 5 LIMIT 1')
  work_order_flow = cur.fetchone()
  if not work_order_flow:
    cur.execute(
      '''
      INSERT INTO approval_flows(
        approval_flow_name, process_library_id, approval_type, status, remarks,
        creator, create_by, create_time, update_time, is_deleted
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
      ''',
      ('生产工单审批规则', '', 5, 1, '生产工单默认审批规则', '系统管理员', '1', t, t),
    )
    cur.execute(
      '''
      SELECT id
      FROM approval_flows
      WHERE is_deleted = 0 AND approval_type = 5 AND approval_flow_name = ?
      ORDER BY id DESC
      LIMIT 1
      ''',
      ('生产工单审批规则',),
    )
    work_order_flow_row = cur.fetchone()
    work_order_flow_id = safe_int(work_order_flow_row['id'] if work_order_flow_row else 0, 0)
    cur.executemany(
      '''
      INSERT INTO approval_flow_nodes(
        approval_flow_id, approval_node_name, role_id, approval_ids, node_index, remarks, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      [
        (work_order_flow_id, '生产主管审批', '1', '1', 1, '默认节点1', t, t),
        (work_order_flow_id, '计划复核', '1', '1', 2, '默认节点2', t, t),
      ],
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM approval_flow_results')
  approval_result_cnt = int(cur.fetchone()['cnt'])
  if approval_result_cnt == 0:
    cur.execute(
      '''
      INSERT INTO approval_flow_results(
        order_id, result_type, order_scheduling_id, order_name, product_name, process_library_id,
        approval_flow_id, process_people, approval_status, approval_remarks, creator, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      (
        'ORDER-001',
        1,
        'SCHED-001',
        '示例工单',
        '示例产品',
        '1',
        default_tech_flow_id or 1,
        '1',
        3,
        '',
        '系统管理员',
        t,
      ),
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM work_orders')
  work_order_cnt = int(cur.fetchone()['cnt'])
  if work_order_cnt == 0:
    work_order_seed = [
      (
        'wo-1',
        'WO-20260302-001',
        'ct-1',
        'CT-20260302-001',
        '示例客户A',
        'prd-1',
        'P-CTRL-001',
        '控制模块A',
        100.0,
        110.0,
        100.0,
        60.0,
        4,
        1,
        '2026-03-06',
        '2026-03-25',
        '2026-03-07 09:00:00',
        '2026-03-24 18:00:00',
        '系统管理员',
        0,
        0,
        '待继续入库示例工单',
        t,
        t,
      ),
      (
        'wo-2',
        'WO-20260302-002',
        'ct-2',
        'CT-20260302-002',
        '示例客户B',
        'prd-3',
        'P-SNS-003',
        '传感组件C',
        200.0,
        120.0,
        110.0,
        0.0,
        3,
        2,
        '2026-03-10',
        '2026-04-05',
        '2026-03-12 08:30:00',
        '',
        '系统管理员',
        0,
        0,
        '生产中示例工单',
        t,
        t,
      ),
      (
        'wo-3',
        'WO-20260302-003',
        'ct-1',
        'CT-20260302-001',
        '示例客户A',
        'prd-2',
        'P-PWR-002',
        '电源模块B',
        50.0,
        50.0,
        50.0,
        50.0,
        5,
        2,
        '2026-03-01',
        '2026-03-12',
        '2026-03-02 09:20:00',
        '2026-03-11 17:40:00',
        '系统管理员',
        0,
        0,
        '已完结示例工单',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO work_orders(
        id, work_order_no, contract_id, contract_no, customer_name, product_id, product_code, product_name,
        plan_quantity, reported_quantity, qualified_quantity, inbound_quantity, status, priority,
        planned_start_date, planned_end_date, actual_start_time, actual_end_time,
        applicant, approval_flow_id, current_node_index, remark, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      work_order_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM work_reports')
  work_report_cnt = int(cur.fetchone()['cnt'])
  if work_report_cnt == 0:
    work_report_seed = [
      ('wr-1', 'wo-1', 'WO-20260302-001', '组装', 60.0, 55.0, 5.0, '1', '系统管理员', '2026-03-10 10:00:00', '', t),
      ('wr-2', 'wo-1', 'WO-20260302-001', '测试', 50.0, 45.0, 5.0, '1', '系统管理员', '2026-03-14 15:30:00', '', t),
      ('wr-3', 'wo-2', 'WO-20260302-002', '装配', 120.0, 110.0, 10.0, '1', '系统管理员', '2026-03-16 11:20:00', '', t),
    ]
    cur.executemany(
      '''
      INSERT INTO work_reports(
        id, work_order_id, work_order_no, process_name, report_quantity, qualified_quantity,
        defect_quantity, report_user_id, report_user_name, report_time, remark, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      work_report_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM work_inbounds')
  work_inbound_cnt = int(cur.fetchone()['cnt'])
  if work_inbound_cnt == 0:
    work_inbound_seed = [
      ('wi-1', 'WI-20260302-001', 'wo-1', 'WO-20260302-001', 40.0, '成品仓A', '系统管理员', '2026-03-18 10:10:00', '', t),
      ('wi-2', 'WI-20260302-002', 'wo-1', 'WO-20260302-001', 20.0, '成品仓A', '系统管理员', '2026-03-20 16:00:00', '', t),
      ('wi-3', 'WI-20260302-003', 'wo-3', 'WO-20260302-003', 50.0, '成品仓B', '系统管理员', '2026-03-11 17:50:00', '', t),
    ]
    cur.executemany(
      '''
      INSERT INTO work_inbounds(
        id, inbound_no, work_order_id, work_order_no, quantity,
        warehouse_name, operator_name, inbound_time, remark, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      work_inbound_seed,
    )
