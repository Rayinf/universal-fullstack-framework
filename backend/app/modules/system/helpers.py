from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs

from fastapi import Request

SYSTEM_CONFIG_FIELD_MAP = {
  'companyName': 'company_name',
  'systemName': 'system_name',
  'version': 'version',
}


def parse_form_body(raw_body: str) -> dict[str, str]:
  form = parse_qs(raw_body)
  return {key: str(values[0] if values else '') for key, values in form.items()}


def parse_login_form(raw_body: str) -> tuple[str, str]:
  form = parse_form_body(raw_body)
  username = str(form.get('username', '')).strip()
  password = str(form.get('password', '')).strip()
  return username, password


async def extract_refresh_token(request: Request) -> str:
  raw_body = (await request.body()).decode('utf-8')
  form = parse_form_body(raw_body)
  refresh_token = str(form.get('refresh_token') or form.get('refreshToken') or '').strip()
  if refresh_token:
    return refresh_token

  try:
    payload = await request.json()
  except (ValueError, TypeError, json.JSONDecodeError):
    return ''

  if not isinstance(payload, dict):
    return ''
  return str(payload.get('refresh_token') or payload.get('refreshToken') or '').strip()


def resolve_system_config_column(code: str) -> str | None:
  return SYSTEM_CONFIG_FIELD_MAP.get(code)


def normalize_system_config_payload(payload: dict[str, Any]) -> dict[str, str]:
  return {
    'companyName': str(payload.get('companyName', '')).strip() or '本地制造企业',
    'systemName': str(payload.get('systemName', '')).strip() or 'MES本地版',
    'version': str(payload.get('version', '')).strip() or '1.0.0',
  }
