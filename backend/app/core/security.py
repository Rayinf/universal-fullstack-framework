from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.env import parse_csv_env

MIN_JWT_SECRET_LENGTH = 32
WEAK_JWT_SECRET_VALUES = {
  'change-me',
  'changeme',
  'default',
  'mes',
  'mes123',
  'mes@123',
  'password',
  'admin',
  'admin123',
  '123456',
}
DEFAULT_DEV_CORS_ORIGINS = [
  'http://localhost:5173',
  'http://127.0.0.1:5173',
  'http://localhost:5174',
  'http://127.0.0.1:5174',
  'http://localhost:5175',
  'http://127.0.0.1:5175',
  'http://localhost:5176',
  'http://127.0.0.1:5176',
]
DEFAULT_DEV_CORS_ORIGIN_REGEX = r'^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?$'
PUBLIC_API_PATHS = {
  '/health',
  '/manage/api/systemConfig/getSystemDefaultData',
}
PUBLIC_API_PREFIXES = (
  '/auth/oauth2/token',
  '/auth/oauth2/refresh',
  '/docs',
  '/redoc',
  '/openapi.json',
)


@dataclass(frozen=True)
class CorsConfig:
  allow_origins: list[str]
  allow_origin_regex: str
  allow_credentials: bool


@dataclass(frozen=True)
class SecurityConfig:
  app_env: str
  raw_jwt_secret: str
  jwt_secret_is_ephemeral: bool
  cors_allow_origins: list[str]
  cors_allow_origin_regex: str


def build_cors_config(
  app_env: str,
  raw_allow_origins: str,
  raw_allow_origin_regex: str,
) -> CorsConfig:
  allow_origins = parse_csv_env(raw_allow_origins)
  if not allow_origins:
    allow_origins = [] if app_env == 'production' else DEFAULT_DEV_CORS_ORIGINS.copy()

  allow_origin_regex = raw_allow_origin_regex.strip()
  if not allow_origin_regex and app_env != 'production':
    allow_origin_regex = DEFAULT_DEV_CORS_ORIGIN_REGEX

  return CorsConfig(
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials='*' not in allow_origins,
  )


def should_require_auth(path: str) -> bool:
  if path in PUBLIC_API_PATHS:
    return False
  if any(path.startswith(prefix) for prefix in PUBLIC_API_PREFIXES):
    return False
  return path.startswith('/admin/') or path.startswith('/manage/') or path.startswith('/local/')


def validate_security_config(config: SecurityConfig) -> None:
  if config.app_env != 'production':
    if config.jwt_secret_is_ephemeral:
      print('[WARN] APP_JWT_SECRET 未配置，当前使用临时密钥，仅适用于开发环境。')
    return

  errors: list[str] = []
  jwt_secret_lower = config.raw_jwt_secret.lower()
  if config.jwt_secret_is_ephemeral:
    errors.append('生产环境必须配置 APP_JWT_SECRET。')
  if len(config.raw_jwt_secret) < MIN_JWT_SECRET_LENGTH:
    errors.append(f'APP_JWT_SECRET 长度必须 >= {MIN_JWT_SECRET_LENGTH}。')
  if jwt_secret_lower in WEAK_JWT_SECRET_VALUES:
    errors.append('APP_JWT_SECRET 过于简单，请使用高强度随机字符串。')
  if '*' in config.cors_allow_origins:
    errors.append('生产环境禁止在 APP_CORS_ORIGINS 中配置通配符 *。')
  if not config.cors_allow_origins and not config.cors_allow_origin_regex:
    errors.append('生产环境必须配置 APP_CORS_ORIGINS 或 APP_CORS_ORIGIN_REGEX。')

  if errors:
    details = '; '.join(errors)
    raise RuntimeError(f'[SECURITY] 配置校验失败: {details}')


def create_auth_guard_middleware(
  parse_token_func: Callable[[str, str], dict[str, Any] | None],
) -> Callable[[Request, Callable[[Request], Awaitable[Any]]], Awaitable[Any]]:
  async def auth_guard_middleware(request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:
    path = request.url.path
    if request.method.upper() == 'OPTIONS' or not should_require_auth(path):
      return await call_next(request)

    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').replace('bearer ', '').strip()
    payload = parse_token_func(token, expected_type='access') if token else None
    if not payload:
      return JSONResponse(status_code=401, content={'code': 401, 'msg': '未登录或登录已过期', 'data': None})

    user_id = str(payload.get('sub', '')).strip()
    if not user_id:
      return JSONResponse(status_code=401, content={'code': 401, 'msg': '未登录或登录已过期', 'data': None})

    # 验证单点登录（互踢）机制
    from app.core.session import session_manager
    token_signature = token.split('.')[-1]
    if not session_manager.is_session_valid(user_id, payload.get('iat', 0), token_signature):
        # 424 状态码在前端 request.ts 中已被配置为"被踢出/会话异常"的登出处理
        return JSONResponse(status_code=424, content={'code': 424, 'msg': '您的账号已在其他设备登录，被迫下线', 'data': None})

    request.state.user_id = user_id

    return await call_next(request)

  return auth_guard_middleware
