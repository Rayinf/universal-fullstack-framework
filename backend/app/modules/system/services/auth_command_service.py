from __future__ import annotations

from app.core.session import session_manager
from app.modules.system.deps import AuthRouterDeps
from app.modules.system.repositories.user_repo import (
  fetch_user_by_id,
  fetch_user_by_username,
)
from app.modules.system.serializers import build_token_response
from app.modules.system.services.errors import SystemServiceError


def _register_access_session(deps: AuthRouterDeps, user_id: str, access_token: str) -> None:
  payload = deps.parse_token_func(access_token, 'access')
  if not payload:
    return
  token_signature = access_token.split('.')[-1]
  session_manager.register_session(user_id, payload.get('iat', 0), token_signature)


def _issue_tokens(deps: AuthRouterDeps, user_id: str) -> dict[str, str]:
  access_token = deps.build_token_func(user_id, 'access', deps.access_token_expire_seconds)
  refresh_token = deps.build_token_func(user_id, 'refresh', deps.refresh_token_expire_seconds)
  _register_access_session(deps, user_id, access_token)
  return build_token_response(access_token, refresh_token)


def login_user(deps: AuthRouterDeps, *, username: str, password: str) -> dict[str, str]:
  if not username or not password:
    raise SystemServiceError('用户名或密码不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  user = fetch_user_by_username(cur, username)
  conn.close()

  if not user or not deps.verify_password_func(password, str(user['password'] or '')):
    raise SystemServiceError('用户名或密码错误', 401)

  return _issue_tokens(deps, str(user['user_id']))


def refresh_user_token(deps: AuthRouterDeps, *, refresh_token: str) -> dict[str, str]:
  token_payload = deps.parse_token_func(refresh_token, 'refresh')
  if not token_payload:
    raise SystemServiceError('refresh_token无效或已过期', 401)

  user_id = str(token_payload.get('sub', '')).strip()
  if not user_id:
    raise SystemServiceError('refresh_token无效', 401)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  user = fetch_user_by_id(cur, user_id)
  conn.close()
  if not user:
    raise SystemServiceError('用户不存在', 401)

  return _issue_tokens(deps, user_id)
