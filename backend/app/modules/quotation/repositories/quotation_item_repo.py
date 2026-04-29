from __future__ import annotations

from typing import Any


def fetch_quotation_items(cur: Any, quotation_id: str) -> list[Any]:
  cur.execute(
    '''
    SELECT id, quotation_id, product_id, product_code, product_name, specification, unit,
           quantity, unit_price, amount, sort_order, remark
    FROM quotation_items
    WHERE quotation_id = ?
    ORDER BY sort_order ASC, id ASC
    ''',
    (quotation_id,),
  )
  return cur.fetchall()


def delete_quotation_items(cur: Any, quotation_id: str) -> None:
  cur.execute('DELETE FROM quotation_items WHERE quotation_id = ?', (quotation_id,))


def insert_quotation_item(
  cur: Any,
  *,
  item_id: str,
  quotation_id: str,
  product_id: str,
  product_code: str,
  product_name: str,
  specification: str,
  unit: str,
  quantity: float,
  unit_price: float,
  amount: float,
  sort_order: int,
  remark: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO quotation_items(
      id, quotation_id, product_id, product_code, product_name, specification,
      unit, quantity, unit_price, amount, sort_order, remark
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      item_id,
      quotation_id,
      product_id,
      product_code,
      product_name,
      specification,
      unit,
      quantity,
      unit_price,
      amount,
      sort_order,
      remark,
    ),
  )
