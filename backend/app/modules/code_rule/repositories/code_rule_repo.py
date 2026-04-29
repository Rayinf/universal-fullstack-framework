from __future__ import annotations

from typing import Any


def query_code_rule_page_total(cur: Any, where_sql: str, values: tuple[Any, ...]) -> Any:
  cur.execute(f'SELECT COUNT(1) AS cnt FROM code_rules {where_sql}', values)
  return cur.fetchone()


def query_code_rule_page_rows(cur: Any, where_sql: str, values: tuple[Any, ...], size: int, offset: int) -> list[Any]:
  cur.execute(
    f'''
    SELECT id, type, prefix, rule_name, is_enable, remark, create_time, update_time
    FROM code_rules
    {where_sql}
    ORDER BY type ASC
    LIMIT ? OFFSET ?
    ''',
    (*values, size, offset),
  )
  return cur.fetchall()


def fetch_code_rule_detail(cur: Any, rule_id: str) -> Any:
  cur.execute(
    'SELECT id, type, prefix, rule_name, is_enable, remark, create_time, update_time FROM code_rules WHERE id = ?',
    (rule_id,),
  )
  return cur.fetchone()


def fetch_code_rule_by_id(cur: Any, rule_id: str) -> Any:
  cur.execute('SELECT id FROM code_rules WHERE id = ?', (rule_id,))
  return cur.fetchone()


def fetch_code_rule_by_type(cur: Any, rule_type: int) -> Any:
  cur.execute('SELECT id FROM code_rules WHERE type = ?', (rule_type,))
  return cur.fetchone()


def fetch_code_rule_prefix_by_type(cur: Any, rule_type: int) -> Any:
  cur.execute('SELECT prefix FROM code_rules WHERE type = ?', (rule_type,))
  return cur.fetchone()


def insert_code_rule(
  cur: Any,
  *,
  rule_id: str,
  rule_type: int,
  prefix: str,
  rule_name: str,
  is_enable: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO code_rules(id, type, prefix, rule_name, is_enable, remark, create_time, update_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (rule_id, rule_type, prefix, rule_name, is_enable, remark, now, now),
  )


def update_code_rule(
  cur: Any,
  *,
  rule_id: str,
  rule_type: int,
  prefix: str,
  rule_name: str,
  is_enable: int,
  remark: str,
  now: str,
) -> None:
  cur.execute(
    '''
    UPDATE code_rules
    SET type = ?, prefix = ?, rule_name = ?, is_enable = ?, remark = ?, update_time = ?
    WHERE id = ?
    ''',
    (rule_type, prefix, rule_name, is_enable, remark, now, rule_id),
  )


def update_code_rule_enabled(cur: Any, rule_id: str, is_enable: int, now: str) -> None:
  cur.execute('UPDATE code_rules SET is_enable = ?, update_time = ? WHERE id = ?', (is_enable, now, rule_id))
