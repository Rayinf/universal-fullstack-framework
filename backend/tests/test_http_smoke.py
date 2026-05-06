from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import unittest
import uuid
from pathlib import Path
from urllib import error, parse, request

import psycopg
from psycopg import sql


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def connect_postgres(*, options: str | None = None) -> psycopg.Connection:
  pg_dsn = os.getenv('APP_PG_DSN', os.getenv('MES_PG_DSN', '')).strip()
  connect_kwargs: dict[str, object] = {}
  if pg_dsn:
    connect_kwargs['conninfo'] = pg_dsn
  else:
    connect_kwargs.update(
      host=os.getenv('APP_PG_HOST', os.getenv('MES_PG_HOST', '127.0.0.1')).strip(),
      port=int(os.getenv('APP_PG_PORT', os.getenv('MES_PG_PORT', '5432'))),
      dbname=os.getenv('APP_PG_DATABASE', os.getenv('MES_PG_DATABASE', 'app_local')).strip(),
      user=os.getenv('APP_PG_USER', os.getenv('MES_PG_USER', os.getenv('USER', 'postgres'))).strip(),
      password=os.getenv('APP_PG_PASSWORD', os.getenv('MES_PG_PASSWORD', '')).strip(),
    )
  if options:
    connect_kwargs['options'] = options
  return psycopg.connect(**connect_kwargs)


def pick_free_port() -> int:
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(('127.0.0.1', 0))
    sock.listen(1)
    return int(sock.getsockname()[1])


def read_process_output(process: subprocess.Popen[str]) -> str:
  stdout, _ = process.communicate(timeout=5)
  return stdout or ''


def request_json(
  *,
  method: str,
  url: str,
  headers: dict[str, str] | None = None,
  form_data: dict[str, str] | None = None,
  json_data: dict[str, object] | None = None,
) -> tuple[int, dict[str, object]]:
  data: bytes | None = None
  final_headers = dict(headers or {})
  if form_data is not None:
    data = parse.urlencode(form_data).encode('utf-8')
    final_headers.setdefault('Content-Type', 'application/x-www-form-urlencoded')
  elif json_data is not None:
    data = json.dumps(json_data).encode('utf-8')
    final_headers.setdefault('Content-Type', 'application/json')

  req = request.Request(url, data=data, headers=final_headers, method=method.upper())
  try:
    with request.urlopen(req, timeout=10) as response:
      raw_body = response.read().decode('utf-8')
      return int(response.status), json.loads(raw_body)
  except error.HTTPError as exc:
    raw_body = exc.read().decode('utf-8')
    payload = json.loads(raw_body) if raw_body else {}
    return int(exc.code), payload


class HttpSmokeTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls) -> None:
    cls.schema_name = f"http_smoke_{uuid.uuid4().hex[:12]}"
    cls.port = pick_free_port()
    cls.base_url = f'http://127.0.0.1:{cls.port}'

    admin_conn = connect_postgres(options='-c search_path=public')
    admin_conn.autocommit = True
    with admin_conn.cursor() as cur:
      cur.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(cls.schema_name)))
    admin_conn.close()

    env = os.environ.copy()
    env.setdefault('APP_ENV', 'development')
    env['PGOPTIONS'] = f'-c search_path={cls.schema_name}'

    cls.server_process = subprocess.Popen(
      [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', str(cls.port)],
      cwd=str(BACKEND_ROOT),
      env=env,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      text=True,
    )

    startup_error: str | None = None
    for _ in range(40):
      if cls.server_process.poll() is not None:
        startup_error = read_process_output(cls.server_process)
        break
      try:
        status, payload = request_json(method='GET', url=f'{cls.base_url}/health')
      except Exception:
        time.sleep(0.25)
        continue
      if status == 200 and payload.get('code') == 0:
        return
      time.sleep(0.25)

    if startup_error is None:
      cls.server_process.terminate()
      startup_error = read_process_output(cls.server_process)
    raise AssertionError(f'HTTP smoke 启动失败: {startup_error}')

  @classmethod
  def tearDownClass(cls) -> None:
    process = getattr(cls, 'server_process', None)
    if process is not None and process.poll() is None:
      process.terminate()
      try:
        process.wait(timeout=5)
      except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)

    admin_conn = connect_postgres(options='-c search_path=public')
    admin_conn.autocommit = True
    with admin_conn.cursor() as cur:
      cur.execute(sql.SQL('DROP SCHEMA IF EXISTS {} CASCADE').format(sql.Identifier(cls.schema_name)))
    admin_conn.close()

  def test_http_smoke_login_refresh_and_local_crud_flow(self) -> None:
    unauthorized_status, unauthorized_payload = request_json(
      method='GET',
      url=f'{self.base_url}/admin/user/info',
    )
    self.assertEqual(unauthorized_status, 401)
    self.assertEqual(unauthorized_payload['code'], 401)

    health_status, health_payload = request_json(
      method='GET',
      url=f'{self.base_url}/health',
    )
    self.assertEqual(health_status, 200)
    self.assertEqual(health_payload['code'], 0)
    self.assertEqual(health_payload['data']['status'], 'ok')
    self.assertEqual(health_payload['data']['dbDriver'], 'postgres')

    login_status, login_payload = request_json(
      method='POST',
      url=f'{self.base_url}/auth/oauth2/token',
      form_data={'username': 'admin', 'password': 'admin123'},
    )
    self.assertEqual(login_status, 200)
    access_token = str(login_payload['access_token'])
    refresh_token = str(login_payload['refresh_token'])
    headers = {'Authorization': f'Bearer {access_token}'}

    user_info_status, user_info_payload = request_json(
      method='GET',
      url=f'{self.base_url}/admin/user/info',
      headers=headers,
    )
    self.assertEqual(user_info_status, 200)
    self.assertEqual(user_info_payload['code'], 0)
    self.assertEqual(user_info_payload['data']['sysUser']['username'], 'admin')

    menu_tree_status, menu_tree_payload = request_json(
      method='GET',
      url=f'{self.base_url}/admin/menu/tree',
      headers=headers,
    )
    self.assertEqual(menu_tree_status, 200)
    self.assertEqual(menu_tree_payload['code'], 0)
    self.assertGreater(len(menu_tree_payload['data']), 0)

    crud_page_status, crud_page_payload = request_json(
      method='GET',
      url=f'{self.base_url}/local/crud/page?current=1&size=10',
      headers=headers,
    )
    self.assertEqual(crud_page_status, 200)
    self.assertEqual(crud_page_payload['code'], 0)
    self.assertGreaterEqual(int(crud_page_payload['data']['total']), 2)

    unique_suffix = uuid.uuid4().hex[:8]
    create_status, create_payload = request_json(
      method='POST',
      url=f'{self.base_url}/local/crud',
      headers=headers,
      json_data={
        'name': f'HTTP Smoke {unique_suffix}',
        'code': f'SMOKE-{unique_suffix.upper()}',
        'remark': 'postgres http smoke',
        'status': 0,
      },
    )
    self.assertEqual(create_status, 200)
    self.assertEqual(create_payload['code'], 0)

    refresh_status, refresh_payload = request_json(
      method='POST',
      url=f'{self.base_url}/auth/oauth2/refresh',
      form_data={'refresh_token': refresh_token},
    )
    self.assertEqual(refresh_status, 200)
    self.assertEqual(refresh_payload['code'], 0)
    refreshed_access_token = str(refresh_payload['data']['access_token'])
    self.assertNotEqual(refreshed_access_token, access_token)

    kicked_status, _ = request_json(
      method='GET',
      url=f'{self.base_url}/admin/user/info',
      headers=headers,
    )
    self.assertEqual(kicked_status, 424)

    refreshed_headers = {'Authorization': f'Bearer {refreshed_access_token}'}
    refreshed_user_info_status, refreshed_user_info_payload = request_json(
      method='GET',
      url=f'{self.base_url}/admin/user/info',
      headers=refreshed_headers,
    )
    self.assertEqual(refreshed_user_info_status, 200)
    self.assertEqual(refreshed_user_info_payload['code'], 0)

    filtered_crud_status, filtered_crud_payload = request_json(
      method='GET',
      url=f'{self.base_url}/local/crud/page?current=1&size=10&keyword=SMOKE-{unique_suffix.upper()}',
      headers=refreshed_headers,
    )
    self.assertEqual(filtered_crud_status, 200)
    self.assertEqual(filtered_crud_payload['code'], 0)
    self.assertEqual(int(filtered_crud_payload['data']['total']), 1)


if __name__ == '__main__':
  unittest.main()
