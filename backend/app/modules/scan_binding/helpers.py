from __future__ import annotations

from typing import Any, Callable

from app.modules.scan_binding.deps import ScanBindingRouterDeps


def build_scan_binding_where(keyword: str | None) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []
  if keyword and keyword.strip():
    where_sql += ' AND (scan_asset_number LIKE ? OR identifier LIKE ?)'
    key = f'%{keyword.strip()}%'
    values.extend([key, key])
  return where_sql, values


def resolve_page(current: int | None, page: int | None, size: int) -> tuple[int, int]:
  return max(current or page or 1, 1), max(size, 1)


def parse_scan_binding_payload(
  payload: dict[str, Any],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'record_id': safe_int_func(payload.get('id'), 0),
    'scan_asset_number': str(payload.get('scanAssetNumber', '')).strip(),
    'identifier': str(payload.get('identifier', '')).strip(),
    'process_id': safe_int_func(payload.get('processId'), 0),
  }
