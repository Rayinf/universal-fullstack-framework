from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
  sys.path.insert(0, str(BACKEND_ROOT))

from app.core.auth import JwtTokenCodec
from app.core.openapi import DOC_TAGS, create_custom_openapi
from app.core.security import SecurityConfig, build_cors_config, create_auth_guard_middleware, should_require_auth, validate_security_config


class FakeRequest:
  def __init__(self, path: str, method: str = 'GET', authorization: str = '') -> None:
    self.url = SimpleNamespace(path=path)
    self.method = method
    self.headers = {'Authorization': authorization} if authorization else {}
    self.state = SimpleNamespace()


class CoreHelpersTestCase(unittest.TestCase):
  def test_jwt_token_codec_builds_unique_tokens_within_same_second(self) -> None:
    codec = JwtTokenCodec(secret='test-secret')
    first_token = codec.build_token('u-1', 'access', 60)
    second_token = codec.build_token('u-1', 'access', 60)

    self.assertNotEqual(first_token, second_token)
    self.assertIsNotNone(codec.parse_token(first_token, 'access'))
    self.assertIsNotNone(codec.parse_token(second_token, 'access'))

  def test_build_cors_config_uses_dev_defaults(self) -> None:
    config = build_cors_config(app_env='development', raw_allow_origins='', raw_allow_origin_regex='')
    self.assertIn('http://localhost:5173', config.allow_origins)
    self.assertTrue(config.allow_origin_regex.startswith('^https?://'))
    self.assertTrue(config.allow_credentials)

  def test_should_require_auth_matches_public_and_protected_paths(self) -> None:
    self.assertFalse(should_require_auth('/health'))
    self.assertFalse(should_require_auth('/docs'))
    self.assertTrue(should_require_auth('/admin/user/info'))
    self.assertTrue(should_require_auth('/manage/api/customers/page'))
    self.assertFalse(should_require_auth('/unknown/path'))

  def test_validate_security_config_rejects_invalid_production_settings(self) -> None:
    config = SecurityConfig(
      app_env='production',
      raw_jwt_secret='admin123',
      jwt_secret_is_ephemeral=False,
      cors_allow_origins=[],
      cors_allow_origin_regex='',
    )
    with self.assertRaises(RuntimeError) as ctx:
      validate_security_config(config)
    self.assertIn('MES_JWT_SECRET 长度必须 >= 32', str(ctx.exception))
    self.assertIn('MES_CORS_ORIGINS', str(ctx.exception))

  def test_auth_guard_middleware_rejects_invalid_token(self) -> None:
    middleware = create_auth_guard_middleware(
      parse_token_func=lambda token, expected_type='access': None,
    )

    async def call_next(_request: FakeRequest) -> str:
      return 'ok'

    response = asyncio.run(
      middleware(
        FakeRequest('/admin/user/info', authorization='Bearer bad-token'),
        call_next,
      ),
    )
    self.assertEqual(response.status_code, 401)
    self.assertIn('未登录或登录已过期', response.body.decode('utf-8'))

  def test_auth_guard_middleware_sets_user_id_for_valid_token(self) -> None:
    middleware = create_auth_guard_middleware(
      parse_token_func=lambda token, expected_type='access': {'sub': 'u-1'} if token == 'good-token' else None,
    )

    async def call_next(request: FakeRequest) -> str:
      return request.state.user_id

    result = asyncio.run(
      middleware(
        FakeRequest('/admin/user/info', authorization='Bearer good-token'),
        call_next,
      ),
    )
    self.assertEqual(result, 'u-1')

  def test_custom_openapi_adds_summary_and_tags(self) -> None:
    app = FastAPI(title='Test API', version='1.0.0', openapi_tags=DOC_TAGS)

    @app.get('/health')
    def health() -> dict[str, str]:
      return {'status': 'ok'}

    app.openapi = create_custom_openapi(app)
    schema = app.openapi()
    operation = schema['paths']['/health']['get']
    self.assertEqual(operation['summary'], '健康检查')
    self.assertEqual(operation['tags'], ['系统与认证'])
    self.assertIn('统一返回', operation['description'])


if __name__ == '__main__':
  unittest.main()
