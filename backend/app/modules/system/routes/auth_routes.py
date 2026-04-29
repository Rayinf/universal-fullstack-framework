from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.system.deps import AuthRouterDeps
from app.modules.system.helpers import extract_refresh_token, parse_login_form
from app.modules.system.services.auth_command_service import (
  login_user,
  refresh_user_token,
)
from app.modules.system.services.errors import SystemServiceError


def register_auth_routes(router: APIRouter, deps: AuthRouterDeps) -> None:
  fail_func = deps.fail_func
  ok_func = deps.ok_func

  async def _login(request: Request) -> Any:
    username, password = parse_login_form((await request.body()).decode('utf-8'))
    try:
      return login_user(deps, username=username, password=password)
    except SystemServiceError as error:
      return fail_func(error.message, error.code)

  @router.post('/auth/oauth/token')
  async def login(request: Request) -> Any:
    return await _login(request)

  @router.post('/auth/oauth2/token')
  async def login_oauth2(request: Request) -> Any:
    return await _login(request)

  @router.post('/auth/oauth2/refresh')
  async def refresh_access_token(request: Request) -> Any:
    refresh_token = await extract_refresh_token(request)
    try:
      token_payload = refresh_user_token(deps, refresh_token=refresh_token)
    except SystemServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(token_payload, 'success')
