from __future__ import annotations

from typing import Any

from app.modules.device.deps import DeviceRouterDeps
from app.modules.device.helpers import build_page_filters
from app.modules.device.repositories.device_repo import (
  fetch_device_detail_row,
  query_device_category_rows,
  query_device_list_rows,
  query_device_page_rows,
  query_device_page_total,
)
from app.modules.device.serializers import build_page_result, device_to_dict
from app.modules.device.services.errors import DeviceServiceError


def _build_device_category_map(cur: Any) -> dict[str, str]:
  return {str(row['id']): row['name'] for row in query_device_category_rows(cur)}


def query_device_page(
  deps: DeviceRouterDeps,
  *,
  page: int | None,
  current: int | None,
  size: int,
  keyword: str | None,
  device_category_id: str | None,
  status: int | None,
  workstation_id: str | None,
) -> dict[str, Any]:
  page_current = max(current or page or 1, 1)
  page_size = max(size, 1)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql, values = build_page_filters(keyword, device_category_id, status, workstation_id)
  total = int(query_device_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_device_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  user_map, _, workstation_map = deps.load_name_maps_func(cur)
  asset_type_map = _build_device_category_map(cur)
  conn.close()
  return build_page_result(
    [device_to_dict(row, user_map, workstation_map, asset_type_map) for row in rows],
    total,
    page_current,
    page_size,
  )


def list_devices(deps: DeviceRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_device_list_rows(cur)
  user_map, _, workstation_map = deps.load_name_maps_func(cur)
  asset_type_map = _build_device_category_map(cur)
  conn.close()
  return [device_to_dict(row, user_map, workstation_map, asset_type_map) for row in rows]


def get_device_detail(deps: DeviceRouterDeps, *, device_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_device_detail_row(cur, device_id)
  if not row:
    conn.close()
    raise DeviceServiceError('设备不存在', 404)
  user_map, _, workstation_map = deps.load_name_maps_func(cur)
  asset_type_map = _build_device_category_map(cur)
  conn.close()
  return device_to_dict(row, user_map, workstation_map, asset_type_map)
