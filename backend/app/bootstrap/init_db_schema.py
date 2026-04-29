from __future__ import annotations

from typing import Any

from app.bootstrap.init_db_schema_demo_common import apply_demo_common_schema
from app.bootstrap.init_db_schema_production import apply_production_schema
from app.bootstrap.init_db_schema_sales import apply_sales_schema
from app.bootstrap.init_db_schema_system import apply_system_schema


def apply_bootstrap_schema(cur: Any) -> None:
  apply_system_schema(cur)
  apply_demo_common_schema(cur)
  apply_sales_schema(cur)
  apply_production_schema(cur)
