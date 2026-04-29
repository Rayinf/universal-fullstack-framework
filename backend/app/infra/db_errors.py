from __future__ import annotations

try:
  import psycopg
except ImportError:  # pragma: no cover - 仅在未安装依赖的解释器中兜底
  class DatabaseIntegrityError(Exception):
    pass
else:
  DatabaseIntegrityError = psycopg.IntegrityError
