from __future__ import annotations

from typing import Any, Callable


def seed_sales_data(cur: Any, *, now_str: Callable[[], str]) -> None:
  t = now_str()

  cur.execute('SELECT COUNT(1) AS cnt FROM customers')
  customer_cnt = int(cur.fetchone()['cnt'])
  if customer_cnt == 0:
    customer_seed = [
      (
        'customer-1',
        'CUST-001',
        '示例客户A',
        '张经理',
        '李介绍',
        1,
        '重点战略客户',
        '系统管理员',
        t,
        t,
      ),
      (
        'customer-2',
        'CUST-002',
        '示例客户B',
        '王经理',
        '赵介绍',
        2,
        '常规合作客户',
        '系统管理员',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO customers(
        id, customer_code, customer_name, account_manager_name, introducer_name,
        customer_level, special_notes, creator, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      customer_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM product_catalog')
  product_catalog_cnt = int(cur.fetchone()['cnt'])
  if product_catalog_cnt == 0:
    product_seed = [
      (
        'prd-1',
        'P-CTRL-001',
        '控制模块A',
        'A1-标准版',
        'pcs',
        680.0,
        420.0,
        '控制器',
        1,
        '销售与生产联调示例产品',
        t,
        t,
      ),
      (
        'prd-2',
        'P-PWR-002',
        '电源模块B',
        'B2-48V',
        'pcs',
        320.0,
        210.0,
        '电源',
        1,
        '销售与生产联调示例产品',
        t,
        t,
      ),
      (
        'prd-3',
        'P-SNS-003',
        '传感组件C',
        'C3-高精度',
        'pcs',
        120.0,
        75.0,
        '传感器',
        1,
        '销售与生产联调示例产品',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO product_catalog(
        id, product_code, product_name, specification, unit, reference_price, cost_price,
        category, status, remark, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      product_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM quotations')
  quotation_cnt = int(cur.fetchone()['cnt'])
  if quotation_cnt == 0:
    quotation_seed = [
      (
        'qt-1',
        'QT-20260302-001',
        'customer-1',
        '示例客户A',
        '张经理',
        16000.0,
        95.0,
        15200.0,
        30,
        '2026-04-01',
        2,
        '系统管理员',
        0,
        0,
        1,
        '已审批示例报价',
        t,
        t,
      ),
      (
        'qt-2',
        'QT-20260302-002',
        'customer-2',
        '示例客户B',
        '王经理',
        8600.0,
        100.0,
        8600.0,
        15,
        '2026-03-20',
        1,
        '系统管理员',
        0,
        1,
        1,
        '待审批示例报价',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO quotations(
        id, quote_no, customer_id, customer_name, contact_person, total_amount, discount_rate,
        final_amount, validity_days, validity_end_date, status, applicant, approval_flow_id,
        current_node_index, version, remark, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      quotation_seed,
    )

    quotation_item_seed = [
      ('qti-1', 'qt-1', 'prd-1', 'P-CTRL-001', '控制模块A', 'A1-标准版', 'pcs', 10.0, 800.0, 8000.0, 1, ''),
      ('qti-2', 'qt-1', 'prd-2', 'P-PWR-002', '电源模块B', 'B2-48V', 'pcs', 20.0, 400.0, 8000.0, 2, ''),
      ('qti-3', 'qt-2', 'prd-3', 'P-SNS-003', '传感组件C', 'C3-高精度', 'pcs', 50.0, 172.0, 8600.0, 1, ''),
    ]
    cur.executemany(
      '''
      INSERT INTO quotation_items(
        id, quotation_id, product_id, product_code, product_name, specification,
        unit, quantity, unit_price, amount, sort_order, remark
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      quotation_item_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM contracts')
  contract_cnt = int(cur.fetchone()['cnt'])
  if contract_cnt == 0:
    contract_seed = [
      (
        'ct-1',
        'CT-20260302-001',
        'qt-1',
        'customer-1',
        '示例客户A',
        '控制系统年度供货合同',
        15200.0,
        8000.0,
        '2026-03-02',
        '2026-03-05',
        '2026-12-31',
        '30%预付款，70%验收后支付',
        2,
        0,
        '联调示例合同',
        t,
        t,
      ),
      (
        'ct-2',
        'CT-20260302-002',
        'qt-2',
        'customer-2',
        '示例客户B',
        '传感组件批量采购合同',
        8600.0,
        0.0,
        '2026-03-03',
        '2026-03-10',
        '2026-08-31',
        '验收后一次性回款',
        1,
        0,
        '联调示例合同',
        t,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO contracts(
        id, contract_no, quotation_id, customer_id, customer_name, contract_name,
        total_amount, paid_amount, signed_date, start_date, end_date, payment_terms,
        status, expire_warning_sent, remark, create_time, update_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      contract_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM payment_records')
  payment_cnt = int(cur.fetchone()['cnt'])
  if payment_cnt == 0:
    payment_seed = [
      (
        'pay-1',
        'ct-1',
        'PAY-20260302-001',
        5000.0,
        '2026-03-08',
        1,
        '示例客户A',
        '系统管理员',
        '首笔回款已确认',
        1,
        t,
      ),
      (
        'pay-2',
        'ct-1',
        'PAY-20260302-002',
        3000.0,
        '2026-03-15',
        1,
        '示例客户A',
        '系统管理员',
        '二笔回款已确认',
        1,
        t,
      ),
      (
        'pay-3',
        'ct-2',
        'PAY-20260302-003',
        2000.0,
        '2026-03-18',
        2,
        '示例客户B',
        '系统管理员',
        '待财务确认',
        0,
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO payment_records(
        id, contract_id, payment_no, payment_amount, payment_date, payment_method,
        payer_name, received_by, remark, status, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      payment_seed,
    )

  cur.execute('SELECT COUNT(1) AS cnt FROM commission_records')
  commission_cnt = int(cur.fetchone()['cnt'])
  if commission_cnt == 0:
    commission_seed = [
      (
        'com-1',
        'ct-1',
        'CT-20260302-001',
        '示例客户A',
        '1',
        '系统管理员',
        15200.0,
        8000.0,
        5.0,
        400.0,
        0,
        '',
        '首期佣金待发放',
        t,
      ),
    ]
    cur.executemany(
      '''
      INSERT INTO commission_records(
        id, contract_id, contract_no, customer_name, salesperson_id, salesperson_name,
        contract_amount, payment_amount, commission_rate, commission_amount,
        status, pay_date, remark, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      commission_seed,
    )
