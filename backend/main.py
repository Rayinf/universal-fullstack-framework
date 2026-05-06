from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.bootstrap.router_registry import register_routers
from app.core.auth import JwtTokenCodec, PasswordManager
from app.bootstrap.init_db import init_db as bootstrap_init_db
from app.core.env import load_env_files
from app.core.exception_handlers import register_exception_handlers
from app.core.notifications import (
  create_notification as persist_notification,
  create_notification_for_users as persist_notification_for_users,
)
from app.core.openapi import DOC_TAGS, create_custom_openapi
from app.core.response import ok_response, fail_response
from app.core.runtime_helpers import create_get_current_user, now_str, safe_float, safe_int
from app.core.security import SecurityConfig, build_cors_config, create_auth_guard_middleware, validate_security_config
from app.infra.db import create_database_runtime
from app.modules.system_admin.menu import flatten_menu_ids as modular_flatten_menu_ids, menu_tree as modular_menu_tree

BACKEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_ROOT.parent
UPLOADS_DIR = BACKEND_ROOT / 'uploads'
UPLOADS_DIR.mkdir(exist_ok=True)

load_env_files(PROJECT_ROOT / '.env', BACKEND_ROOT / '.env')


def env_value(name: str, legacy_name: str, default: str = '') -> str:
  return os.getenv(name, os.getenv(legacy_name, default)).strip()


DB_DRIVER = 'postgres'
PG_DSN = env_value('APP_PG_DSN', 'MES_PG_DSN')
PG_HOST = env_value('APP_PG_HOST', 'MES_PG_HOST', '127.0.0.1')
PG_PORT = int(env_value('APP_PG_PORT', 'MES_PG_PORT', '5432'))
PG_DB = env_value('APP_PG_DATABASE', 'MES_PG_DATABASE', 'app_local')
PG_USER = env_value('APP_PG_USER', 'MES_PG_USER', 'postgres')
PG_PASSWORD = env_value('APP_PG_PASSWORD', 'MES_PG_PASSWORD')
APP_ENV = env_value('APP_ENV', 'MES_ENV', os.getenv('ENV', 'development')).lower()
RAW_JWT_SECRET = env_value('APP_JWT_SECRET', 'MES_JWT_SECRET')
JWT_SECRET_IS_EPHEMERAL = not bool(RAW_JWT_SECRET)
JWT_SECRET = RAW_JWT_SECRET or secrets.token_urlsafe(48)
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_SECONDS = int(env_value('APP_ACCESS_TOKEN_EXPIRE_SECONDS', 'MES_ACCESS_TOKEN_EXPIRE_SECONDS', str(8 * 60 * 60)))
REFRESH_TOKEN_EXPIRE_SECONDS = int(env_value('APP_REFRESH_TOKEN_EXPIRE_SECONDS', 'MES_REFRESH_TOKEN_EXPIRE_SECONDS', str(7 * 24 * 60 * 60)))
PASSWORD_HASH_PREFIX = 'pbkdf2_sha256'
PASSWORD_HASH_ITERATIONS = int(env_value('APP_PASSWORD_HASH_ITERATIONS', 'MES_PASSWORD_HASH_ITERATIONS', '200000'))
CORS_CONFIG = build_cors_config(
  app_env=APP_ENV,
  raw_allow_origins=env_value('APP_CORS_ORIGINS', 'MES_CORS_ORIGINS'),
  raw_allow_origin_regex=env_value('APP_CORS_ORIGIN_REGEX', 'MES_CORS_ORIGIN_REGEX'),
)

SECURITY_CONFIG = SecurityConfig(
  app_env=APP_ENV,
  raw_jwt_secret=RAW_JWT_SECRET,
  jwt_secret_is_ephemeral=JWT_SECRET_IS_EPHEMERAL,
  cors_allow_origins=CORS_CONFIG.allow_origins,
  cors_allow_origin_regex=CORS_CONFIG.allow_origin_regex,
)

token_codec = JwtTokenCodec(secret=JWT_SECRET, algorithm=JWT_ALGORITHM)
password_manager = PasswordManager(prefix=PASSWORD_HASH_PREFIX, iterations=PASSWORD_HASH_ITERATIONS)
build_token = token_codec.build_token
parse_token = token_codec.parse_token
is_password_hashed = password_manager.is_password_hashed
hash_password = password_manager.hash_password
verify_password = password_manager.verify_password
db_runtime = create_database_runtime(
  pg_dsn=PG_DSN,
  pg_host=PG_HOST,
  pg_port=PG_PORT,
  pg_db=PG_DB,
  pg_user=PG_USER,
  pg_password=PG_PASSWORD,
  safe_int_func=safe_int,
)
get_conn = db_runtime.get_conn
sync_pg_serial_sequences = db_runtime.sync_pg_serial_sequences

app = FastAPI(
  title='Universal Fullstack Framework Local API',
  version='1.0.0',
  description=(
    '本服务为 Universal Fullstack Framework 本地后端实现。\n\n'
    '- 接口文档已统一为中文说明\n'
    '- 返回结构统一为 `{code, msg, data}`\n'
    '- `code = 0` 表示成功，`msg` 为提示信息，`data` 为业务数据'
  ),
  openapi_tags=DOC_TAGS,
)

app.openapi = create_custom_openapi(app)
register_exception_handlers(app)

app.add_middleware(
  CORSMiddleware,
  allow_origins=CORS_CONFIG.allow_origins,
  allow_origin_regex=CORS_CONFIG.allow_origin_regex or None,
  allow_credentials=CORS_CONFIG.allow_credentials,
  allow_methods=['*'],
  allow_headers=['*'],
)


def ok(data: Any = None, msg: str = 'success') -> dict[str, Any]:
  return ok_response(data=data, msg=msg)


def fail(msg: str, code: int = 500) -> JSONResponse:
  return fail_response(msg=msg, code=code, status_code=200)


get_current_user = create_get_current_user(get_conn_func=get_conn, parse_token_func=parse_token)


def create_notification(
  user_id: str,
  title: str,
  content: str = '',
  ntype: int = 3,
  biz_type: str = '',
  biz_id: str = '',
) -> None:
  persist_notification(
    user_id,
    title,
    content,
    ntype,
    biz_type,
    biz_id,
    get_conn_func=get_conn,
    now_str_func=now_str,
  )


def create_notification_for_users(
  user_ids: list[str],
  title: str,
  content: str = '',
  ntype: int = 3,
  biz_type: str = '',
  biz_id: str = '',
) -> None:
  persist_notification_for_users(
    user_ids,
    title,
    content,
    ntype,
    biz_type,
    biz_id,
    get_conn_func=get_conn,
    now_str_func=now_str,
  )


def init_db() -> None:
  bootstrap_init_db(
    get_conn=get_conn,
    now_str=now_str,
    safe_int=safe_int,
    hash_password=hash_password,
    is_password_hashed=is_password_hashed,
    _sync_pg_serial_sequences=sync_pg_serial_sequences,
    menu_tree=modular_menu_tree,
    flatten_menu_ids=modular_flatten_menu_ids,
  )


register_routers(
  app,
  db_driver=DB_DRIVER,
  uploads_dir=UPLOADS_DIR,
  menu_tree_func=modular_menu_tree,
  ok_func=ok,
  fail_func=fail,
  get_conn_func=get_conn,
  now_str_func=now_str,
  safe_int_func=safe_int,
  safe_float_func=safe_float,
  get_current_user_func=get_current_user,
  verify_password_func=verify_password,
  build_token_func=build_token,
  parse_token_func=parse_token,
  access_token_expire_seconds=ACCESS_TOKEN_EXPIRE_SECONDS,
  refresh_token_expire_seconds=REFRESH_TOKEN_EXPIRE_SECONDS,
  hash_password_func=hash_password,
  create_notification_for_users_func=create_notification_for_users,
)

app.middleware('http')(create_auth_guard_middleware(parse_token_func=parse_token))


@app.on_event('startup')
def startup_event() -> None:
  validate_security_config(SECURITY_CONFIG)
  init_db()


# ═══════════════════════════════════════════════════════════════════
# Phase 0 – 通用基础设施 API
# ═══════════════════════════════════════════════════════════════════


if __name__ == '__main__':
  import uvicorn

  uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
