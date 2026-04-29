from __future__ import annotations

import importlib
import re
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class DatabaseConfig:
  pg_dsn: str
  pg_host: str
  pg_port: int
  pg_db: str
  pg_user: str
  pg_password: str
  psycopg: Any = None
  dict_row: Any = None


def _legacy_sql_to_postgres_sql(sql: str, params: Any = ()) -> tuple[str, Any]:
  text = str(sql or '')
  p = params

  pragma_match = re.match(
    r"\s*PRAGMA\s+table_info\((['\"]?)([a-zA-Z_][\w]*)\1\)\s*;?\s*$",
    text,
    re.IGNORECASE,
  )
  if pragma_match:
    table_name = pragma_match.group(2)
    return (
      'SELECT column_name AS name FROM information_schema.columns '
      'WHERE table_schema = current_schema() AND table_name = %s ORDER BY ordinal_position',
      (table_name,),
    )

  has_insert_ignore = bool(re.search(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', text, re.IGNORECASE))
  if has_insert_ignore:
    text = re.sub(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', 'INSERT INTO', text, flags=re.IGNORECASE)
    if 'ON CONFLICT' not in text.upper():
      text = text.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING'

  text = re.sub(
    r'\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b',
    'SERIAL PRIMARY KEY',
    text,
    flags=re.IGNORECASE,
  )

  if '?' in text:
    text = text.replace('?', '%s')

  return text, p


class PgCursorAdapter:
  def __init__(self, cursor: Any):
    self._cursor = cursor
    self.lastrowid = None

  def execute(self, sql: str, params: Any = ()) -> Any:
    pg_sql, pg_params = _legacy_sql_to_postgres_sql(sql, params)
    self._cursor.execute(pg_sql, pg_params)
    return self

  def executemany(self, sql: str, seq_of_params: Any) -> Any:
    pg_sql, _ = _legacy_sql_to_postgres_sql(sql, ())
    self._cursor.executemany(pg_sql, seq_of_params)
    return self

  def fetchone(self) -> Any:
    return self._cursor.fetchone()

  def fetchall(self) -> Any:
    return self._cursor.fetchall()

  @property
  def rowcount(self) -> int:
    return int(getattr(self._cursor, 'rowcount', -1))


class PgConnectionAdapter:
  def __init__(self, conn: Any):
    self._conn = conn

  def cursor(self) -> PgCursorAdapter:
    return PgCursorAdapter(self._conn.cursor())

  def commit(self) -> None:
    self._conn.commit()

  def rollback(self) -> None:
    self._conn.rollback()

  def close(self) -> None:
    self._conn.close()


class DatabaseRuntime:
  def __init__(self, config: DatabaseConfig, safe_int_func: Callable[[Any, int], int]):
    self.config = config
    self.safe_int_func = safe_int_func

  def sync_pg_serial_sequences(self, cur: Any) -> None:
    serial_tables = [
      'basic_infos',
      'scan_binding_processes',
      'code_rules',
      'sys_log_users',
      'sys_backup_infos',
      'approval_flows',
      'approval_flow_nodes',
      'approval_flow_results',
    ]
    for table_name in serial_tables:
      cur.execute('SELECT pg_get_serial_sequence(?, ?) AS seq_name', (table_name, 'id'))
      seq_row = cur.fetchone()
      seq_name = str(seq_row['seq_name'] or '').strip() if seq_row else ''
      if not seq_name:
        continue

      cur.execute(f'SELECT COALESCE(MAX(id), 0) AS max_id FROM {table_name}')
      max_id = self.safe_int_func(cur.fetchone()['max_id'], 0)
      cur.execute('SELECT setval(?::regclass, ?, true)', (seq_name, max_id))

  def get_conn(self) -> Any:
    if self.config.psycopg is None or self.config.dict_row is None:
      raise RuntimeError('未安装 psycopg，请先执行: pip install -r backend/requirements.txt')
    if self.config.pg_dsn:
      conn = self.config.psycopg.connect(self.config.pg_dsn, row_factory=self.config.dict_row)
    else:
      conn = self.config.psycopg.connect(
        host=self.config.pg_host,
        port=self.config.pg_port,
        dbname=self.config.pg_db,
        user=self.config.pg_user,
        password=self.config.pg_password,
        row_factory=self.config.dict_row,
      )
    return PgConnectionAdapter(conn)


def create_database_runtime(
  *,
  pg_dsn: str,
  pg_host: str,
  pg_port: int,
  pg_db: str,
  pg_user: str,
  pg_password: str,
  safe_int_func: Callable[[Any, int], int],
) -> DatabaseRuntime:
  try:
    psycopg = importlib.import_module('psycopg')
    dict_row = importlib.import_module('psycopg.rows').dict_row
  except ImportError:
    psycopg = None
    dict_row = None

  config = DatabaseConfig(
    pg_dsn=pg_dsn,
    pg_host=pg_host,
    pg_port=pg_port,
    pg_db=pg_db,
    pg_user=pg_user,
    pg_password=pg_password,
    psycopg=psycopg,
    dict_row=dict_row,
  )
  return DatabaseRuntime(config=config, safe_int_func=safe_int_func)
