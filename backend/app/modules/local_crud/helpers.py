from __future__ import annotations

from typing import Any


def build_keyword_filter(keyword: str | None) -> tuple[str, list[str]]:
  keyword_text = str(keyword or '').strip()
  if not keyword_text:
    return '', []
  like_value = f'%{keyword_text}%'
  return ' AND (name LIKE ? OR code LIKE ?)', [like_value, like_value]


def parse_crud_payload(payload: dict[str, Any]) -> dict[str, Any]:
  return {
    'name': str(payload.get('name', '')).strip(),
    'code': str(payload.get('code', '')).strip(),
    'remark': str(payload.get('remark', '')).strip(),
    'status': int(payload.get('status') or 0),
  }
