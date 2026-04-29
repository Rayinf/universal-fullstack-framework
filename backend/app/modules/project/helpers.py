from __future__ import annotations

from typing import Any, Callable


def build_project_page_filters(keyword: str | None, status: int | None) -> tuple[str, list[Any]]:
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  if keyword and keyword.strip():
    keyword_text = keyword.strip()
    where_sql += ' AND (project_name LIKE ? OR project_code LIKE ? OR owner_name LIKE ?)'
    values.extend([f'%{keyword_text}%', f'%{keyword_text}%', f'%{keyword_text}%'])
  if status is not None and status >= 0:
    where_sql += ' AND status = ?'
    values.append(status)

  return where_sql, values


def clamp_progress(progress: int) -> int:
  return max(min(progress, 100), 0)


def parse_project_payload(
  payload: dict[str, Any],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'project_code': str(payload.get('projectCode', '')).strip(),
    'project_name': str(payload.get('projectName', '')).strip(),
    'owner_name': str(payload.get('ownerName', '')).strip(),
    'priority': safe_int_func(payload.get('priority'), 2),
    'project_status': safe_int_func(payload.get('status'), 0),
    'progress': safe_int_func(payload.get('progress'), 0),
    'start_date': str(payload.get('startDate', '')).strip(),
    'end_date': str(payload.get('endDate', '')).strip(),
    'remark': str(payload.get('remark', '')).strip(),
  }
