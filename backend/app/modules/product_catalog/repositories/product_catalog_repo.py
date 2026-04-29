from __future__ import annotations

from typing import Any


def query_product_catalog_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM product_catalog {where_sql}', values)
  return cur.fetchone()


def query_product_catalog_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, product_code, product_name, specification, unit, reference_price, cost_price,
           category, status, remark, create_time, update_time
    FROM product_catalog
    {where_sql}
    ORDER BY update_time DESC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def query_enabled_product_catalog_rows(cur: Any) -> list[Any]:
  cur.execute(
    '''
    SELECT id, product_code, product_name, specification, unit, reference_price, cost_price,
           category, status, remark, create_time, update_time
    FROM product_catalog
    WHERE status = 1
    ORDER BY product_code ASC, update_time DESC
    ''',
  )
  return cur.fetchall()


def insert_product_catalog(
  cur: Any,
  *,
  product_id: str,
  product_code: str,
  product_name: str,
  specification: str,
  unit: str,
  reference_price: float,
  cost_price: float,
  category: str,
  status: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO product_catalog(
      id, product_code, product_name, specification, unit, reference_price, cost_price,
      category, status, remark, create_time, update_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
      product_id,
      product_code,
      product_name,
      specification,
      unit,
      reference_price,
      cost_price,
      category,
      status,
      remark,
      now,
      now,
    ),
  )


def update_product_catalog(
  cur: Any,
  *,
  product_id: str,
  product_code: str,
  product_name: str,
  specification: str,
  unit: str,
  reference_price: float,
  cost_price: float,
  category: str,
  status: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE product_catalog
    SET product_code = ?, product_name = ?, specification = ?, unit = ?,
        reference_price = ?, cost_price = ?, category = ?, status = ?, remark = ?, update_time = ?
    WHERE id = ?
    ''',
    (
      product_code,
      product_name,
      specification,
      unit,
      reference_price,
      cost_price,
      category,
      status,
      remark,
      now,
      product_id,
    ),
  )


def delete_product_catalog(cur: Any, product_id: str) -> None:
  cur.execute('DELETE FROM product_catalog WHERE id = ?', (product_id,))
