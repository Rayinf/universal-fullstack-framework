from __future__ import annotations

from typing import Any, Callable


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  pages = (total + size - 1) // size if size > 0 else 0
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': pages,
  }


def contract_to_dict(
  row: Any,
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'contractNo': row['contract_no'] or '',
    'quotationId': row['quotation_id'] or '',
    'customerId': row['customer_id'] or '',
    'customerName': row['customer_name'] or '',
    'contractName': row['contract_name'] or '',
    'totalAmount': safe_float_func(row['total_amount']),
    'paidAmount': safe_float_func(row['paid_amount']),
    'signedDate': row['signed_date'] or '',
    'startDate': row['start_date'] or '',
    'endDate': row['end_date'] or '',
    'paymentTerms': row['payment_terms'] or '',
    'status': safe_int_func(row['status'], 0),
    'expireWarningSent': safe_int_func(row['expire_warning_sent'], 0),
    'remark': row['remark'] or '',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def payment_to_dict(
  row: Any,
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'contractId': row['contract_id'] or '',
    'paymentNo': row['payment_no'] or '',
    'paymentAmount': safe_float_func(row['payment_amount']),
    'paymentDate': row['payment_date'] or '',
    'paymentMethod': safe_int_func(row['payment_method'], 1),
    'payerName': row['payer_name'] or '',
    'receivedBy': row['received_by'] or '',
    'remark': row['remark'] or '',
    'status': safe_int_func(row['status'], 0),
    'createTime': row['create_time'] or '',
    'contractNo': row['contract_no'] or '',
    'customerName': row['customer_name'] or '',
  }


def commission_to_dict(
  row: Any,
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'contractId': row['contract_id'] or '',
    'contractNo': row['contract_no'] or '',
    'customerName': row['customer_name'] or '',
    'salespersonId': row['salesperson_id'] or '',
    'salespersonName': row['salesperson_name'] or '',
    'contractAmount': safe_float_func(row['contract_amount']),
    'paymentAmount': safe_float_func(row['payment_amount']),
    'commissionRate': safe_float_func(row['commission_rate']),
    'commissionAmount': safe_float_func(row['commission_amount']),
    'status': safe_int_func(row['status'], 0),
    'payDate': row['pay_date'] or '',
    'remark': row['remark'] or '',
    'createTime': row['create_time'] or '',
  }
