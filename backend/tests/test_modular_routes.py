from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
  sys.path.insert(0, str(BACKEND_ROOT))

from app.core.response import fail_response, ok_response
from app.modules.approval_flow.router import create_approval_flow_router
from app.modules.attachments.router import create_attachment_router
from app.modules.basic_info.router import create_basic_info_router
from app.modules.code_rule.router import create_code_rule_router
from app.modules.contracts.router import create_contract_router
from app.modules.customer.router import create_customer_router
from app.modules.device.router import create_device_router
from app.modules.inventory.router import create_inventory_router
from app.modules.local_crud.router import create_local_crud_router
from app.modules.notifications.router import create_notification_router
from app.modules.process.router import create_process_library_router
from app.modules.product_catalog.router import create_product_catalog_router
from app.modules.project.router import create_project_router
from app.modules.purchase_order.router import create_purchase_order_router
from app.modules.quotation.router import create_quotation_router
from app.modules.scan_binding.router import create_scan_binding_router
from app.modules.sys_backup.router import create_sys_backup_router
from app.modules.sys_log.router import create_sys_log_router
from app.modules.system.router import create_system_router
from app.modules.system.auth_router import create_auth_router
from app.modules.system.config_router import create_system_config_router
from app.modules.system_admin.dept_router import create_dept_read_router
from app.modules.system_admin.dept_write_router import create_dept_write_router
from app.modules.system_admin.role_router import create_role_router
from app.modules.system_admin.router import create_system_admin_router
from app.modules.system_admin.user_router import create_user_router
from app.modules.work_order.router import create_work_order_router
from app.modules.workstation.router import create_workstation_router


def get_route_endpoint(router: Any, path: str, method: str = 'GET') -> Any:
  target_method = method.upper()
  for route in router.routes:
    methods = getattr(route, 'methods', set()) or set()
    if getattr(route, 'path', None) == path and target_method in methods:
      return route.endpoint
  raise AssertionError(f'Route not found: {method} {path}')


class FakeCursor:
  def __init__(self, rows: list[dict[str, Any]]):
    self._rows = rows
    self.executed_sql = ''
    self.executed_params: tuple[Any, ...] = ()

  def execute(self, sql: str, params: tuple[Any, ...]) -> None:
    self.executed_sql = sql
    self.executed_params = params

  def fetchall(self) -> list[dict[str, Any]]:
    return self._rows


class FakeConnection:
  def __init__(self, rows: list[dict[str, Any]]):
    self.cursor_instance = FakeCursor(rows)
    self.closed = False

  def cursor(self) -> FakeCursor:
    return self.cursor_instance

  def close(self) -> None:
    self.closed = True


class ScriptedDeptCursor:
  def __init__(self) -> None:
    self.step = -1
    self.sql_history: list[tuple[str, Any]] = []

  def execute(self, sql: str, params: Any = ()) -> None:
    self.step += 1
    self.sql_history.append((sql, params))

  def fetchone(self) -> dict[str, Any]:
    if self.step == 0:
      return {'cnt': 2}
    return {'cnt': 0}

  def fetchall(self) -> list[dict[str, Any]]:
    if self.step == 1:
      return [
        {
          'dept_id': '10',
          'name': '研发部',
          'parent_id': '1',
          'sort_order': 1,
          'enabled': 1,
          'create_time': '2026-03-01 00:00:00',
          'update_time': '2026-03-02 00:00:00',
        },
        {
          'dept_id': '11',
          'name': '质量部',
          'parent_id': '1',
          'sort_order': 2,
          'enabled': 1,
          'create_time': '2026-03-01 00:00:00',
          'update_time': '2026-03-02 00:00:00',
        },
      ]
    if self.step == 2:
      return [
        {'dept_id': '1', 'name': '总部'},
        {'dept_id': '10', 'name': '研发部'},
        {'dept_id': '11', 'name': '质量部'},
      ]
    return []


class ScriptedDeptConnection:
  def __init__(self) -> None:
    self.cursor_instance = ScriptedDeptCursor()
    self.closed = False

  def cursor(self) -> ScriptedDeptCursor:
    return self.cursor_instance

  def close(self) -> None:
    self.closed = True


class QueueCursor:
  def __init__(self, one_queue: list[Any] | None = None, all_queue: list[list[dict[str, Any]]] | None = None):
    self.one_queue = one_queue or []
    self.all_queue = all_queue or []
    self.sql_history: list[tuple[str, Any]] = []
    self.executemany_history: list[tuple[str, Any]] = []

  def execute(self, sql: str, params: Any = ()) -> None:
    self.sql_history.append((sql, params))

  def executemany(self, sql: str, seq_of_params: Any) -> None:
    params_list = list(seq_of_params)
    self.executemany_history.append((sql, params_list))

  def fetchone(self) -> Any:
    if self.one_queue:
      return self.one_queue.pop(0)
    return None

  def fetchall(self) -> list[dict[str, Any]]:
    if self.all_queue:
      return self.all_queue.pop(0)
    return []


class QueueConnection:
  def __init__(self, cursor: QueueCursor):
    self.cursor_instance = cursor
    self.closed = False
    self.commit_count = 0
    self.rollback_count = 0

  def cursor(self) -> QueueCursor:
    return self.cursor_instance

  def close(self) -> None:
    self.closed = True

  def commit(self) -> None:
    self.commit_count += 1

  def rollback(self) -> None:
    self.rollback_count += 1


class JsonRequest:
  def __init__(self, payload: Any):
    self._payload = payload

  async def json(self) -> Any:
    return self._payload


class UploadRequest(JsonRequest):
  pass


class BodyRequest:
  def __init__(self, body: bytes, json_payload: Any | Exception | None = None):
    self._body = body
    self._json_payload = json_payload if json_payload is not None else ValueError('no json body')

  async def body(self) -> bytes:
    return self._body

  async def json(self) -> Any:
    if isinstance(self._json_payload, Exception):
      raise self._json_payload
    return self._json_payload


class FakeUploadFile:
  def __init__(self, filename: str, content: bytes):
    self.filename = filename
    self._content = content

  async def read(self) -> bytes:
    return self._content


def _ok_wrapper(data: Any, msg: str = 'success') -> dict[str, Any]:
  return ok_response(data=data, msg=msg)


class ModularRoutesTestCase(unittest.TestCase):
  def test_ok_and_fail_response_shape(self) -> None:
    ok_data = ok_response({'k': 'v'})
    self.assertEqual(ok_data['code'], 0)
    self.assertEqual(ok_data['msg'], 'success')
    self.assertEqual(ok_data['data'], {'k': 'v'})

    fail_body = bytes(fail_response('bad request', code=400).body)
    fail_data = fail_body.decode('utf-8')
    self.assertIn('"code":400', fail_data)
    self.assertIn('"msg":"bad request"', fail_data)

  def test_system_router_health(self) -> None:
    router = create_system_router(ok_func=_ok_wrapper, db_driver='postgres')
    health_endpoint = get_route_endpoint(router, '/health')
    result = health_endpoint()
    self.assertEqual(result['code'], 0)
    self.assertEqual(result['data']['status'], 'ok')
    self.assertEqual(result['data']['dbDriver'], 'postgres')

  def test_auth_router_login_and_refresh_validation(self) -> None:
    login_conn = QueueConnection(
      QueueCursor(one_queue=[{'user_id': 'u-1', 'password': 'hashed::123456'}]),
    )
    router = create_auth_router(
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      ok_func=_ok_wrapper,
      get_conn_func=lambda: login_conn,
      verify_password_func=lambda raw, hashed: hashed == f'hashed::{raw}',
      build_token_func=lambda user_id, token_type, expire: f'{token_type}:{user_id}:{expire}',
      parse_token_func=lambda token, expected_type='refresh': {'sub': 'u-1'} if token.startswith('refresh:') else None,
      access_token_expire_seconds=60,
      refresh_token_expire_seconds=120,
    )
    login_endpoint = get_route_endpoint(router, '/auth/oauth/token', 'POST')
    login_oauth2_endpoint = get_route_endpoint(router, '/auth/oauth2/token', 'POST')
    refresh_endpoint = get_route_endpoint(router, '/auth/oauth2/refresh', 'POST')

    login_result = asyncio.run(login_endpoint(BodyRequest(b'username=alice&password=123456')))
    self.assertEqual(login_result['token_type'], 'Bearer')
    self.assertIn('access:u-1', login_result['access_token'])

    login_oauth2_conn = QueueConnection(
      QueueCursor(one_queue=[{'user_id': 'u-1', 'password': 'hashed::123456'}]),
    )
    oauth2_router = create_auth_router(
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      ok_func=_ok_wrapper,
      get_conn_func=lambda: login_oauth2_conn,
      verify_password_func=lambda raw, hashed: hashed == f'hashed::{raw}',
      build_token_func=lambda user_id, token_type, expire: f'{token_type}:{user_id}:{expire}',
      parse_token_func=lambda token, expected_type='refresh': {'sub': 'u-1'} if token.startswith('refresh:') else None,
      access_token_expire_seconds=60,
      refresh_token_expire_seconds=120,
    )
    login_oauth2_endpoint = get_route_endpoint(oauth2_router, '/auth/oauth2/token', 'POST')
    login_oauth2_result = asyncio.run(login_oauth2_endpoint(BodyRequest(b'username=alice&password=123456')))
    self.assertEqual(login_oauth2_result['token_type'], 'Bearer')
    self.assertIn('access:u-1', login_oauth2_result['access_token'])

    refresh_conn = QueueConnection(QueueCursor(one_queue=[{'user_id': 'u-1'}]))
    refresh_router = create_auth_router(
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      ok_func=_ok_wrapper,
      get_conn_func=lambda: refresh_conn,
      verify_password_func=lambda raw, hashed: True,
      build_token_func=lambda user_id, token_type, expire: f'{token_type}:{user_id}:{expire}',
      parse_token_func=lambda token, expected_type='refresh': {'sub': 'u-1'} if token.startswith('refresh:') else None,
      access_token_expire_seconds=60,
      refresh_token_expire_seconds=120,
    )
    refresh_endpoint = get_route_endpoint(refresh_router, '/auth/oauth2/refresh', 'POST')
    refresh_result = asyncio.run(refresh_endpoint(BodyRequest(b'refresh_token=refresh:u-1:120')))
    self.assertEqual(refresh_result['code'], 0)
    self.assertIn('refresh:u-1', refresh_result['data']['refresh_token'])

  def test_auth_router_failure_and_json_refresh_paths(self) -> None:
    router = create_auth_router(
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      ok_func=_ok_wrapper,
      get_conn_func=lambda: QueueConnection(QueueCursor()),
      verify_password_func=lambda raw, hashed: hashed == f'hashed::{raw}',
      build_token_func=lambda user_id, token_type, expire: f'{token_type}:{user_id}:{expire}',
      parse_token_func=lambda token, expected_type='refresh': {'sub': 'u-json'} if token.startswith('refresh-json:') else None,
      access_token_expire_seconds=60,
      refresh_token_expire_seconds=120,
    )
    login_endpoint = get_route_endpoint(router, '/auth/oauth/token', 'POST')
    login_result = asyncio.run(login_endpoint(BodyRequest(b'username=&password=')))
    self.assertEqual(login_result['code'], 400)
    self.assertEqual(login_result['msg'], '用户名或密码不能为空')

    refresh_endpoint = get_route_endpoint(router, '/auth/oauth2/refresh', 'POST')
    invalid_refresh_result = asyncio.run(refresh_endpoint(BodyRequest(b'refresh_token=bad-token')))
    self.assertEqual(invalid_refresh_result['code'], 401)
    self.assertEqual(invalid_refresh_result['msg'], 'refresh_token无效或已过期')

    json_conn = QueueConnection(QueueCursor(one_queue=[{'user_id': 'u-json'}]))
    json_router = create_auth_router(
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      ok_func=_ok_wrapper,
      get_conn_func=lambda: json_conn,
      verify_password_func=lambda raw, hashed: True,
      build_token_func=lambda user_id, token_type, expire: f'{token_type}:{user_id}:{expire}',
      parse_token_func=lambda token, expected_type='refresh': {'sub': 'u-json'} if token.startswith('refresh-json:') else None,
      access_token_expire_seconds=60,
      refresh_token_expire_seconds=120,
    )
    json_refresh_endpoint = get_route_endpoint(json_router, '/auth/oauth2/refresh', 'POST')
    json_refresh_result = asyncio.run(
      json_refresh_endpoint(BodyRequest(b'', json_payload={'refreshToken': 'refresh-json:u-json:120'})),
    )
    self.assertEqual(json_refresh_result['code'], 0)
    self.assertIn('access:u-json', json_refresh_result['data']['access_token'])

  def test_auth_router_wrong_password_and_refresh_missing_user(self) -> None:
    wrong_password_conn = QueueConnection(
      QueueCursor(one_queue=[{'user_id': 'u-1', 'password': 'hashed::123456'}]),
    )
    wrong_password_router = create_auth_router(
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      ok_func=_ok_wrapper,
      get_conn_func=lambda: wrong_password_conn,
      verify_password_func=lambda raw, hashed: False,
      build_token_func=lambda user_id, token_type, expire: f'{token_type}:{user_id}:{expire}',
      parse_token_func=lambda token, expected_type='refresh': None,
      access_token_expire_seconds=60,
      refresh_token_expire_seconds=120,
    )
    login_endpoint = get_route_endpoint(wrong_password_router, '/auth/oauth/token', 'POST')
    login_result = asyncio.run(login_endpoint(BodyRequest(b'username=alice&password=bad-password')))
    self.assertEqual(login_result['code'], 401)
    self.assertEqual(login_result['msg'], '用户名或密码错误')

    refresh_conn = QueueConnection(QueueCursor(one_queue=[None]))
    refresh_router = create_auth_router(
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      ok_func=_ok_wrapper,
      get_conn_func=lambda: refresh_conn,
      verify_password_func=lambda raw, hashed: True,
      build_token_func=lambda user_id, token_type, expire: f'{token_type}:{user_id}:{expire}',
      parse_token_func=lambda token, expected_type='refresh': {'sub': 'ghost'} if token.startswith('refresh:') else None,
      access_token_expire_seconds=60,
      refresh_token_expire_seconds=120,
    )
    refresh_endpoint = get_route_endpoint(refresh_router, '/auth/oauth2/refresh', 'POST')
    refresh_result = asyncio.run(refresh_endpoint(BodyRequest(b'refresh_token=refresh:ghost:120')))
    self.assertEqual(refresh_result['code'], 401)
    self.assertEqual(refresh_result['msg'], '用户不存在')

  def test_system_config_router_read_and_update_validation(self) -> None:
    read_conn = QueueConnection(
      QueueCursor(one_queue=[{'company_name': '测试公司', 'system_name': '测试系统', 'version': '1.2.3'}]),
    )
    router = create_system_config_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: read_conn,
    )
    get_default = get_route_endpoint(router, '/manage/api/systemConfig/getSystemDefaultData')
    read_result = get_default()
    self.assertEqual(read_result['data']['companyName'], '测试公司')

    update_single = get_route_endpoint(router, '/manage/api/systemConfig/update', 'PUT')
    bad_result = asyncio.run(update_single(JsonRequest({'code': '', 'value': 'x'})))
    self.assertEqual(bad_result['code'], 400)

  def test_system_config_router_tenant_and_update_paths(self) -> None:
    conn = QueueConnection(QueueCursor())
    router = create_system_config_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: conn,
    )
    get_tenant_name = get_route_endpoint(router, '/manage/api/tenant/getTenantName')
    tenant_result = get_tenant_name()
    self.assertEqual(tenant_result['code'], 0)
    self.assertEqual(tenant_result['data'], '本地MES租户')

    update_single = get_route_endpoint(router, '/manage/api/systemConfig/update', 'PUT')
    unsupported_result = asyncio.run(update_single(JsonRequest({'code': 'unsupported', 'value': 'x'})))
    self.assertEqual(unsupported_result['code'], 400)
    self.assertEqual(unsupported_result['msg'], '不支持的配置项')

    update_all = get_route_endpoint(router, '/manage/api/systemConfig/updateSystemDefaultData', 'POST')
    update_result = asyncio.run(
      update_all(JsonRequest({'companyName': '新公司', 'systemName': '新系统', 'version': '9.9.9'})),
    )
    self.assertEqual(update_result['code'], 0)
    self.assertEqual(conn.commit_count, 1)
    self.assertIn('UPDATE system_config SET company_name = ?, system_name = ?, version = ? WHERE id = 1', conn.cursor_instance.sql_history[-1][0])

  def test_system_config_router_default_values_and_single_update_success(self) -> None:
    conn = QueueConnection(QueueCursor(one_queue=[None]))
    router = create_system_config_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: conn,
    )
    get_default = get_route_endpoint(router, '/manage/api/systemConfig/getSystemDefaultData')
    default_result = get_default()
    self.assertEqual(default_result['code'], 0)
    self.assertEqual(default_result['data']['companyName'], '本地制造企业')
    self.assertEqual(default_result['data']['systemName'], 'MES本地版')
    self.assertEqual(default_result['data']['version'], '1.0.0')

    update_single = get_route_endpoint(router, '/manage/api/systemConfig/update', 'PUT')
    update_result = asyncio.run(update_single(JsonRequest({'code': 'systemName', 'value': 'MES v2'})))
    self.assertEqual(update_result['code'], 0)
    self.assertEqual(conn.commit_count, 1)
    self.assertIn('UPDATE system_config SET system_name = ? WHERE id = 1', conn.cursor_instance.sql_history[-1][0])

  def test_customer_router_page_and_save_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 'c-1',
              'customer_code': 'CUS-001',
              'customer_name': '客户A',
              'account_manager_name': '张三',
              'introducer_name': '李四',
              'customer_level': 2,
              'special_notes': '重点客户',
              'creator': '系统管理员',
              'create_time': '2026-03-01 00:00:00',
              'update_time': '2026-03-02 00:00:00',
            },
          ],
        ],
      ),
    )
    page_router = create_customer_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/manage/api/customers/page')
    page_result = page_endpoint(current=1, size=10, searchKey='客户')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['customerName'], '客户A')

    save_conn = QueueConnection(QueueCursor())
    save_router = create_customer_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: save_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    save_endpoint = get_route_endpoint(save_router, '/manage/api/customers/save', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'customerCode': '', 'customerName': ''})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_workstation_router_page_and_save_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 'ws-1',
              'workstation_no': 101,
              'workstation_name': '装配工位',
              'workstation_type': 1,
              'status': 1,
              'responsible_person': 'u-1',
              'dept_id': 'd-1',
              'process_library_id': 'p-1',
              'remarks': '',
              'create_time': '2026-03-01 00:00:00',
              'update_time': '2026-03-02 00:00:00',
            },
          ],
          [{'user_id': 'u-1', 'real_name': 'Alice', 'username': 'alice'}],
          [{'dept_id': 'd-1', 'name': '制造部'}],
          [{'id': 'ws-1', 'workstation_name': '装配工位'}],
        ],
      ),
    )
    def load_name_maps(cur: Any) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
      cur.execute('SELECT user_id, real_name, username FROM users')
      user_map = {str(row['user_id']): (row['real_name'] or row['username']) for row in cur.fetchall()}
      cur.execute('SELECT dept_id, name FROM depts')
      dept_map = {str(row['dept_id']): row['name'] for row in cur.fetchall()}
      cur.execute('SELECT id, workstation_name FROM workstations')
      workstation_map = {str(row['id']): row['workstation_name'] for row in cur.fetchall()}
      return user_map, dept_map, workstation_map

    page_router = create_workstation_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      load_name_maps_func=load_name_maps,
    )
    page_endpoint = get_route_endpoint(page_router, '/manage/api/workstation/page')
    page_result = page_endpoint(current=1, size=10, keywords='装配')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['deptName'], '制造部')

    save_conn = QueueConnection(QueueCursor())
    save_router = create_workstation_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: save_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      load_name_maps_func=load_name_maps,
    )
    save_endpoint = get_route_endpoint(save_router, '/manage/api/workstation/save', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'workstationNo': 0, 'workstationName': ''})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_device_router_page_and_save_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 'dev-1',
              'device_name': '焊接机',
              'device_number': 'EQ-001',
              'model': 'X1',
              'device_category_id': 'cat-1',
              'workstation_id': 'ws-1',
              'responsible_person': 'u-1',
              'status': 1,
              'remarks': '',
              'scrap_reason': '',
              'create_time': '2026-03-01 00:00:00',
              'update_time': '2026-03-02 00:00:00',
            },
          ],
          [{'user_id': 'u-1', 'real_name': 'Alice', 'username': 'alice'}],
          [{'dept_id': 'd-1', 'name': '制造部'}],
          [{'id': 'ws-1', 'workstation_name': '装配工位'}],
          [{'id': 'cat-1', 'name': '焊接设备'}],
        ],
      ),
    )

    def load_name_maps(cur: Any) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
      cur.execute('SELECT user_id, real_name, username FROM users')
      user_map = {str(row['user_id']): (row['real_name'] or row['username']) for row in cur.fetchall()}
      cur.execute('SELECT dept_id, name FROM depts')
      dept_map = {str(row['dept_id']): row['name'] for row in cur.fetchall()}
      cur.execute('SELECT id, workstation_name FROM workstations')
      workstation_map = {str(row['id']): row['workstation_name'] for row in cur.fetchall()}
      return user_map, dept_map, workstation_map

    page_router = create_device_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      load_name_maps_func=load_name_maps,
    )
    page_endpoint = get_route_endpoint(page_router, '/manage/api/deviceInfo/page')
    page_result = page_endpoint(current=1, size=10, keyWord='焊接')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['workstationName'], '装配工位')
    self.assertEqual(page_result['data']['records'][0]['deviceCategoryName'], '焊接设备')

    save_conn = QueueConnection(QueueCursor())
    save_router = create_device_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: save_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      load_name_maps_func=load_name_maps,
    )
    save_endpoint = get_route_endpoint(save_router, '/manage/api/deviceInfo/save', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'deviceName': '', 'deviceNumber': '', 'model': ''})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_process_library_router_page_and_list(self) -> None:
    router = create_process_library_router(ok_func=_ok_wrapper)
    page_endpoint = get_route_endpoint(router, '/manage/api/processLibrary/page')
    list_endpoint = get_route_endpoint(router, '/manage/api/processLibrary/list')

    page_result = page_endpoint(current=1, size=10, keyword='标准')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['total'], 1)
    self.assertEqual(page_result['data']['records'][0]['processName'], '标准工序')

    list_result = list_endpoint()
    self.assertEqual(list_result['code'], 0)
    self.assertGreaterEqual(len(list_result['data']), 2)

  def test_process_library_router_pagination_bounds(self) -> None:
    router = create_process_library_router(ok_func=_ok_wrapper)
    page_endpoint = get_route_endpoint(router, '/manage/api/processLibrary/page')

    second_page_result = page_endpoint(current=2, size=1)
    self.assertEqual(second_page_result['code'], 0)
    self.assertEqual(second_page_result['data']['current'], 2)
    self.assertEqual(second_page_result['data']['size'], 1)
    self.assertEqual(second_page_result['data']['pages'], 2)
    self.assertEqual(second_page_result['data']['records'][0]['processName'], '检验工序')

    normalized_result = page_endpoint(current=0, size=0)
    self.assertEqual(normalized_result['code'], 0)
    self.assertEqual(normalized_result['data']['current'], 1)
    self.assertEqual(normalized_result['data']['size'], 1)

  def test_process_library_router_pagination_edges(self) -> None:
    router = create_process_library_router(ok_func=_ok_wrapper)
    page_endpoint = get_route_endpoint(router, '/manage/api/processLibrary/page')

    normalized_result = page_endpoint(current=0, size=0)
    self.assertEqual(normalized_result['code'], 0)
    self.assertEqual(normalized_result['data']['current'], 1)
    self.assertEqual(normalized_result['data']['size'], 1)
    self.assertEqual(normalized_result['data']['pages'], 2)

    next_page_result = page_endpoint(current=2, size=1)
    self.assertEqual(next_page_result['data']['records'][0]['id'], '2')

    empty_result = page_endpoint(current=1, size=10, keyword='不存在')
    self.assertEqual(empty_result['data']['total'], 0)
    self.assertEqual(empty_result['data']['records'], [])
    self.assertEqual(empty_result['data']['pages'], 0)

  def test_local_crud_router_page_and_mutations(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[
          {
            'id': 'crud-1',
            'name': '演示记录',
            'code': 'CRUD-001',
            'remark': '备注',
            'status': 0,
            'create_time': '2026-03-01 00:00:00',
            'update_time': '2026-03-02 00:00:00',
          },
        ]],
      ),
    )
    page_router = create_local_crud_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    page_endpoint = get_route_endpoint(page_router, '/local/crud/page')
    page_result = page_endpoint(current=1, size=10, keyword='演示')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['code'], 'CRUD-001')

    create_conn = QueueConnection(QueueCursor())
    create_router = create_local_crud_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    create_endpoint = get_route_endpoint(create_router, '/local/crud', 'POST')
    create_result = asyncio.run(
      create_endpoint(JsonRequest({'name': '演示记录', 'code': 'CRUD-002', 'remark': '新增', 'status': 0})),
    )
    self.assertEqual(create_result['code'], 0)
    self.assertIn('INSERT INTO crud_items', create_conn.cursor_instance.sql_history[0][0])

    update_conn = QueueConnection(QueueCursor(one_queue=[{'id': 'crud-1'}]))
    update_router = create_local_crud_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: update_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    update_endpoint = get_route_endpoint(update_router, '/local/crud/{item_id}', 'PUT')
    update_result = asyncio.run(
      update_endpoint('crud-1', JsonRequest({'name': '已更新', 'code': 'CRUD-001', 'remark': '修改', 'status': 1})),
    )
    self.assertEqual(update_result['code'], 0)
    self.assertIn('UPDATE crud_items', update_conn.cursor_instance.sql_history[1][0])

    delete_conn = QueueConnection(QueueCursor())
    delete_router = create_local_crud_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: delete_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    delete_endpoint = get_route_endpoint(delete_router, '/local/crud/{item_id}', 'DELETE')
    delete_result = delete_endpoint('crud-1')
    self.assertEqual(delete_result['code'], 0)
    self.assertIn('DELETE FROM crud_items', delete_conn.cursor_instance.sql_history[0][0])

  def test_project_router_page_and_mutations(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[
          {
            'id': 'proj-1',
            'project_code': 'PRJ-001',
            'project_name': 'MES 升级',
            'owner_name': 'Alice',
            'priority': 1,
            'status': 1,
            'progress': 60,
            'start_date': '2026-03-01',
            'end_date': '2026-03-31',
            'remark': '重点项目',
            'create_time': '2026-03-01 00:00:00',
            'update_time': '2026-03-02 00:00:00',
          },
        ]],
      ),
    )
    page_router = create_project_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/local/projects/page')
    page_result = page_endpoint(current=1, size=10, keyword='MES', status=1)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['projectCode'], 'PRJ-001')

    create_conn = QueueConnection(QueueCursor())
    create_router = create_project_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    create_endpoint = get_route_endpoint(create_router, '/local/projects', 'POST')
    create_result = asyncio.run(
      create_endpoint(JsonRequest({'projectCode': 'PRJ-002', 'projectName': '新项目', 'progress': 120})),
    )
    self.assertEqual(create_result['code'], 0)
    self.assertIn('INSERT INTO projects', create_conn.cursor_instance.sql_history[0][0])

    update_conn = QueueConnection(QueueCursor(one_queue=[{'id': 'proj-1'}]))
    update_router = create_project_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: update_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    update_endpoint = get_route_endpoint(update_router, '/local/projects/{project_id}', 'PUT')
    update_result = asyncio.run(
      update_endpoint('proj-1', JsonRequest({'projectCode': 'PRJ-001', 'projectName': 'MES 升级版', 'progress': 88})),
    )
    self.assertEqual(update_result['code'], 0)
    self.assertIn('UPDATE projects', update_conn.cursor_instance.sql_history[1][0])

  def test_purchase_order_router_page_and_flow(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[
          {
            'id': 'po-1',
            'order_no': 'PO-001',
            'supplier_name': '供应商A',
            'item_name': '钢板',
            'quantity': 10,
            'unit_price': 12.5,
            'total_amount': 125,
            'status': 0,
            'applicant': '张三',
            'remark': '',
            'create_time': '2026-03-01 00:00:00',
            'update_time': '2026-03-02 00:00:00',
          },
        ]],
      ),
    )
    page_router = create_purchase_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '审批人', 'username': 'approver'},
    )
    page_endpoint = get_route_endpoint(page_router, '/local/purchase-orders/page')
    page_result = page_endpoint(current=1, size=10, keyword='供应商', status=0)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['orderNo'], 'PO-001')

    submit_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'status': 0}, {'id': 11}],
        all_queue=[[{'id': 21, 'approval_node_name': '采购经理', 'role_id': '', 'approval_ids': 'u-1', 'node_index': 1}]],
      ),
    )
    submit_router = create_purchase_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: submit_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '审批人', 'username': 'approver'},
    )
    submit_endpoint = get_route_endpoint(submit_router, '/local/purchase-orders/{order_id}/submit', 'POST')
    submit_result = submit_endpoint('po-1')
    self.assertEqual(submit_result['code'], 0)
    self.assertIn('UPDATE purchase_orders', submit_conn.cursor_instance.sql_history[-1][0])

    approve_conn = QueueConnection(
      QueueCursor(
        one_queue=[
          {'status': 1, 'approval_flow_id': 11, 'current_node_index': 1},
          {'id': 21, 'approval_node_name': '采购经理', 'role_id': '', 'approval_ids': 'u-1', 'node_index': 1},
          {'max_node': 1},
        ],
      ),
    )
    approve_router = create_purchase_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: approve_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '审批人', 'username': 'approver'},
    )
    approve_endpoint = get_route_endpoint(approve_router, '/local/purchase-orders/{order_id}/approve', 'POST')
    approve_result = approve_endpoint('po-1', SimpleNamespace())
    self.assertEqual(approve_result['code'], 0)
    self.assertEqual(approve_result['msg'], '审批完成')

    status_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'id': 'po-1', 'order_no': 'PO-001', 'status': 1, 'approval_flow_id': 11, 'current_node_index': 1}],
        all_queue=[
          [{'id': 21, 'approval_node_name': '采购经理', 'role_id': '', 'approval_ids': 'u-1', 'node_index': 1}],
          [],
          [{'role_id': 'r-1', 'role_name': '采购经理'}],
          [{'user_id': 'u-1', 'real_name': '审批人', 'username': 'approver'}],
        ],
      ),
    )
    status_router = create_purchase_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: status_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '审批人', 'username': 'approver'},
    )
    status_endpoint = get_route_endpoint(status_router, '/local/purchase-orders/{order_id}/approval-status')
    status_result = status_endpoint('po-1')
    self.assertEqual(status_result['code'], 0)
    self.assertEqual(status_result['data']['nodes'][0]['nodeName'], '采购经理')

  def test_inventory_router_page_and_transaction(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[
          {
            'id': 'item-1',
            'sku': 'MAT-001',
            'item_name': '钢板',
            'unit': 'kg',
            'stock_qty': 50,
            'safety_qty': 20,
            'create_time': '2026-03-01 00:00:00',
            'update_time': '2026-03-02 00:00:00',
          },
        ]],
      ),
    )
    page_router = create_inventory_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/local/inventory/items/page')
    page_result = page_endpoint(current=1, size=10, keyword='钢')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['sku'], 'MAT-001')

    summary_conn = QueueConnection(
      QueueCursor(
        all_queue=[[
          {
            'id': 'item-1',
            'sku': 'MAT-001',
            'item_name': '钢板',
            'unit': 'kg',
            'stock_qty': 10,
            'safety_qty': 20,
            'create_time': '2026-03-01 00:00:00',
            'update_time': '2026-03-02 00:00:00',
          },
        ]],
      ),
    )
    summary_router = create_inventory_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: summary_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
    )
    summary_endpoint = get_route_endpoint(summary_router, '/local/inventory/summary')
    summary_result = summary_endpoint(lowStockOnly=1)
    self.assertEqual(summary_result['code'], 0)
    self.assertTrue(summary_result['data'][0]['isLowStock'])

    tx_conn = QueueConnection(QueueCursor(one_queue=[{'id': 'item-1', 'sku': 'MAT-001', 'item_name': '钢板', 'stock_qty': 50}]))
    tx_router = create_inventory_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: tx_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
    )
    tx_endpoint = get_route_endpoint(tx_router, '/local/inventory/transactions', 'POST')
    tx_result = asyncio.run(tx_endpoint(JsonRequest({'itemId': 'item-1', 'direction': 1, 'quantity': 5, 'businessNo': 'IN-1'})))
    self.assertEqual(tx_result['code'], 0)
    self.assertIn('UPDATE inventory_items', tx_conn.cursor_instance.sql_history[1][0])

  def test_product_catalog_router_page_and_mutations(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'prod-1',
          'product_code': 'P-001',
          'product_name': '主机',
          'specification': 'A1',
          'unit': '台',
          'reference_price': 1000,
          'cost_price': 700,
          'category': '设备',
          'status': 1,
          'remark': '',
          'create_time': '2026-03-01 00:00:00',
          'update_time': '2026-03-02 00:00:00',
        }]],
      ),
    )
    page_router = create_product_catalog_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/local/product-catalog/page')
    page_result = page_endpoint(current=1, size=10, keyword='主机', status=1)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['productCode'], 'P-001')

    create_conn = QueueConnection(QueueCursor())
    create_router = create_product_catalog_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
    )
    create_endpoint = get_route_endpoint(create_router, '/local/product-catalog', 'POST')
    create_result = asyncio.run(create_endpoint(JsonRequest({'productCode': 'P-002', 'productName': '分机'})))
    self.assertEqual(create_result['code'], 0)
    self.assertIn('INSERT INTO product_catalog', create_conn.cursor_instance.sql_history[0][0])

  def test_quotation_router_page_and_flow(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'qt-1',
          'quote_no': 'QT-001',
          'customer_id': 'c-1',
          'customer_name': '客户A',
          'contact_person': '李四',
          'total_amount': 100,
          'discount_rate': 100,
          'final_amount': 100,
          'validity_days': 30,
          'validity_end_date': '2026-03-31',
          'status': 0,
          'applicant': '销售员',
          'approval_flow_id': 0,
          'current_node_index': 0,
          'version': 1,
          'remark': '',
          'create_time': '2026-03-01 00:00:00',
          'update_time': '2026-03-02 00:00:00',
        }]],
      ),
    )
    page_router = create_quotation_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '销售员', 'username': 'sales'},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    page_endpoint = get_route_endpoint(page_router, '/local/quotations/page')
    page_result = page_endpoint(current=1, size=10, keyword='客户', status=0)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['quoteNo'], 'QT-001')

    detail_conn = QueueConnection(
      QueueCursor(
        one_queue=[{
          'id': 'qt-1',
          'quote_no': 'QT-001',
          'customer_id': 'c-1',
          'customer_name': '客户A',
          'contact_person': '李四',
          'total_amount': 100,
          'discount_rate': 100,
          'final_amount': 100,
          'validity_days': 30,
          'validity_end_date': '2026-03-31',
          'status': 0,
          'applicant': '销售员',
          'approval_flow_id': 0,
          'current_node_index': 0,
          'version': 1,
          'remark': '',
          'create_time': '2026-03-01 00:00:00',
          'update_time': '2026-03-02 00:00:00',
        }],
        all_queue=[[{
          'id': 'item-1',
          'quotation_id': 'qt-1',
          'product_id': 'prod-1',
          'product_code': 'P-001',
          'product_name': '主机',
          'specification': 'A1',
          'unit': '台',
          'quantity': 1,
          'unit_price': 100,
          'amount': 100,
          'sort_order': 1,
          'remark': '',
        }]],
      ),
    )
    detail_router = create_quotation_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: detail_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '销售员', 'username': 'sales'},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    detail_endpoint = get_route_endpoint(detail_router, '/local/quotations/{quotation_id}')
    detail_result = detail_endpoint('qt-1')
    self.assertEqual(detail_result['code'], 0)
    self.assertEqual(detail_result['data']['items'][0]['productCode'], 'P-001')

    notifications: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    submit_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'id': 'qt-1', 'status': 0}, {'id': 12}],
        all_queue=[[{'id': 21, 'approval_node_name': '销售经理', 'role_id': '', 'approval_ids': 'u-2', 'node_index': 1}]],
      ),
    )
    submit_router = create_quotation_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: submit_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '销售员', 'username': 'sales'},
      create_notification_for_users_func=lambda *args, **kwargs: notifications.append((args, kwargs)),
    )
    submit_endpoint = get_route_endpoint(submit_router, '/local/quotations/{quotation_id}/submit', 'POST')
    submit_result = submit_endpoint('qt-1')
    self.assertEqual(submit_result['code'], 0)
    self.assertEqual(len(notifications), 1)

    approve_conn = QueueConnection(
      QueueCursor(
        one_queue=[
          {'status': 1, 'approval_flow_id': 12, 'current_node_index': 1},
          {'id': 21, 'approval_node_name': '销售经理', 'role_id': '', 'approval_ids': 'u-2', 'node_index': 1},
        ],
        all_queue=[[{'node_index': 1}]],
      ),
    )
    approve_router = create_quotation_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: approve_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-2', 'real_name': '经理', 'username': 'manager'},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    approve_endpoint = get_route_endpoint(approve_router, '/local/quotations/{quotation_id}/approve', 'POST')
    approve_result = approve_endpoint('qt-1', SimpleNamespace())
    self.assertEqual(approve_result['code'], 0)

    status_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'id': 'qt-1', 'quote_no': 'QT-001', 'status': 1, 'approval_flow_id': 12, 'current_node_index': 1}],
        all_queue=[
          [{'id': 21, 'approval_node_name': '销售经理', 'role_id': '', 'approval_ids': 'u-2', 'node_index': 1}],
          [],
          [{'role_id': 'r-1', 'role_name': '销售经理'}],
          [{'user_id': 'u-2', 'real_name': '经理', 'username': 'manager'}],
        ],
      ),
    )
    status_router = create_quotation_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: status_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '销售员', 'username': 'sales'},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    status_endpoint = get_route_endpoint(status_router, '/local/quotations/{quotation_id}/approval-status')
    status_result = status_endpoint('qt-1')
    self.assertEqual(status_result['code'], 0)
    self.assertEqual(status_result['data']['nodes'][0]['nodeName'], '销售经理')

  def test_contract_router_page_and_expiring(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'ct-1',
          'contract_no': 'CT-001',
          'quotation_id': 'qt-1',
          'customer_id': 'c-1',
          'customer_name': '客户A',
          'contract_name': '年度合同',
          'total_amount': 1000,
          'paid_amount': 200,
          'signed_date': '2026-03-01',
          'start_date': '2026-03-01',
          'end_date': '2026-04-01',
          'payment_terms': '30天',
          'status': 1,
          'expire_warning_sent': 0,
          'remark': '',
          'create_time': '2026-03-01 00:00:00',
          'update_time': '2026-03-02 00:00:00',
        }]],
      ),
    )
    page_router = create_contract_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '财务', 'username': 'finance'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    page_endpoint = get_route_endpoint(page_router, '/local/contracts/page')
    page_result = page_endpoint(current=1, size=10, keyword='客户', status=1)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['contractNo'], 'CT-001')

    notifications: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    expiring_conn = QueueConnection(
      QueueCursor(
        all_queue=[[{
          'id': 'ct-1',
          'contract_no': 'CT-001',
          'customer_name': '客户A',
          'end_date': '2026-03-20',
          'status': 1,
          'expire_warning_sent': 0,
        }]],
      ),
    )
    expiring_router = create_contract_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: expiring_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: None,
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: notifications.append((args, kwargs)),
    )
    expiring_endpoint = get_route_endpoint(expiring_router, '/local/contracts/check-expiring')
    expiring_result = expiring_endpoint(days=15)
    self.assertEqual(expiring_result['code'], 0)
    self.assertEqual(expiring_result['data']['newWarnings'], 1)
    self.assertEqual(len(notifications), 1)

  def test_payment_router_page_and_confirm(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'pm-1',
          'contract_id': 'ct-1',
          'payment_no': 'PM-001',
          'payment_amount': 500,
          'payment_date': '2026-03-05',
          'payment_method': 1,
          'payer_name': '客户A',
          'received_by': '财务',
          'remark': '',
          'status': 0,
          'create_time': '2026-03-05 00:00:00',
          'contract_no': 'CT-001',
          'customer_name': '客户A',
        }]],
      ),
    )
    page_router = create_contract_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '财务', 'username': 'finance'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    page_endpoint = get_route_endpoint(page_router, '/local/payments/page')
    page_result = page_endpoint(current=1, size=10, contractId='ct-1', status=0)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['paymentNo'], 'PM-001')

    confirm_conn = QueueConnection(
      QueueCursor(
        one_queue=[
          {'contract_id': 'ct-1', 'status': 0},
          {'paid': 1000},
          {'total_amount': 1000},
        ],
      ),
    )
    confirm_router = create_contract_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: confirm_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': '财务', 'username': 'finance'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    confirm_endpoint = get_route_endpoint(confirm_router, '/local/payments/{payment_id}/confirm', 'POST')
    confirm_result = confirm_endpoint('pm-1')
    self.assertEqual(confirm_result['code'], 0)
    self.assertIn('UPDATE contracts SET status = 3', confirm_conn.cursor_instance.sql_history[-1][0])

  def test_commission_router_page_and_calculate(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'cm-1',
          'contract_id': 'ct-1',
          'contract_no': 'CT-001',
          'customer_name': '客户A',
          'salesperson_id': 'u-9',
          'salesperson_name': '销售甲',
          'contract_amount': 1000,
          'payment_amount': 500,
          'commission_rate': 10,
          'commission_amount': 50,
          'status': 0,
          'pay_date': '',
          'remark': '',
          'create_time': '2026-03-05 00:00:00',
        }]],
      ),
    )
    page_router = create_contract_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: None,
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    page_endpoint = get_route_endpoint(page_router, '/local/commissions/page')
    page_result = page_endpoint(current=1, size=10, status=0, salespersonName='销售')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['commissionAmount'], 50.0)

    calculate_conn = QueueConnection(
      QueueCursor(one_queue=[{'contract_no': 'CT-001', 'customer_name': '客户A', 'total_amount': 1000, 'paid_amount': 500}]),
    )
    calculate_router = create_contract_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: calculate_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: None,
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    calculate_endpoint = get_route_endpoint(calculate_router, '/local/commissions/calculate/{contract_id}', 'POST')
    calculate_result = asyncio.run(
      calculate_endpoint('ct-1', JsonRequest({'salespersonId': 'u-9', 'salespersonName': '销售甲', 'commissionRate': 10})),
    )
    self.assertEqual(calculate_result['code'], 0)
    self.assertEqual(calculate_result['data']['commissionAmount'], 50.0)

  def test_work_order_router_page_and_flow(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'wo-1',
          'work_order_no': 'WO-001',
          'contract_id': 'ct-1',
          'contract_no': 'CT-001',
          'customer_name': '客户A',
          'product_id': 'prod-1',
          'product_code': 'P-001',
          'product_name': '主机',
          'plan_quantity': 10,
          'reported_quantity': 4,
          'qualified_quantity': 4,
          'inbound_quantity': 0,
          'status': 3,
          'priority': 2,
          'planned_start_date': '2026-03-05',
          'planned_end_date': '2026-03-10',
          'actual_start_time': '2026-03-05 08:00:00',
          'actual_end_time': '',
          'applicant': '申请人',
          'approval_flow_id': 15,
          'current_node_index': 0,
          'remark': '',
          'create_time': '2026-03-05 00:00:00',
          'update_time': '2026-03-05 12:00:00',
        }]],
      ),
    )
    page_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-2', 'real_name': '审批人', 'username': 'approver'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    page_endpoint = get_route_endpoint(page_router, '/local/work-orders/page')
    page_result = page_endpoint(current=1, size=10, keyword='主机', status=3)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['workOrderNo'], 'WO-001')

    notifications: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    submit_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'id': 'wo-1', 'status': 0}, {'id': 15}],
        all_queue=[[{'id': 31, 'approval_node_name': '生产经理', 'role_id': '', 'approval_ids': 'u-2', 'node_index': 1}]],
      ),
    )
    submit_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: submit_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-2', 'real_name': '审批人', 'username': 'approver'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: notifications.append((args, kwargs)),
    )
    submit_endpoint = get_route_endpoint(submit_router, '/local/work-orders/{work_order_id}/submit', 'POST')
    submit_result = submit_endpoint('wo-1')
    self.assertEqual(submit_result['code'], 0)
    self.assertEqual(len(notifications), 1)

    approve_conn = QueueConnection(
      QueueCursor(
        one_queue=[
          {'status': 1, 'approval_flow_id': 15, 'current_node_index': 1, 'applicant': '申请人', 'work_order_no': 'WO-001'},
          {'id': 31, 'approval_node_name': '生产经理', 'role_id': '', 'approval_ids': 'u-2', 'node_index': 1},
        ],
        all_queue=[[{'node_index': 1}]],
      ),
    )
    approve_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: approve_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-2', 'real_name': '审批人', 'username': 'approver'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    approve_endpoint = get_route_endpoint(approve_router, '/local/work-orders/{work_order_id}/approve', 'POST')
    approve_result = approve_endpoint('wo-1', SimpleNamespace())
    self.assertEqual(approve_result['code'], 0)

    status_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'id': 'wo-1', 'work_order_no': 'WO-001', 'status': 1, 'approval_flow_id': 15, 'current_node_index': 1}],
        all_queue=[
          [{'id': 31, 'approval_node_name': '生产经理', 'role_id': '', 'approval_ids': 'u-2', 'node_index': 1}],
          [],
          [{'role_id': 'r-1', 'role_name': '生产经理'}],
          [{'user_id': 'u-2', 'real_name': '审批人', 'username': 'approver'}],
        ],
      ),
    )
    status_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: status_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-2', 'real_name': '审批人', 'username': 'approver'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    status_endpoint = get_route_endpoint(status_router, '/local/work-orders/{work_order_id}/approval-status')
    status_result = status_endpoint('wo-1')
    self.assertEqual(status_result['code'], 0)
    self.assertEqual(status_result['data']['nodes'][0]['nodeName'], '生产经理')

  def test_work_report_router_page_and_create(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'wr-1',
          'work_order_id': 'wo-1',
          'work_order_no': 'WO-001',
          'process_name': '装配',
          'report_quantity': 10,
          'qualified_quantity': 10,
          'defect_quantity': 0,
          'report_user_id': 'u-3',
          'report_user_name': '报工员',
          'report_time': '2026-03-05 10:00:00',
          'remark': '',
          'create_time': '2026-03-05 10:00:00',
          'product_name': '主机',
          'customer_name': '客户A',
        }]],
      ),
    )
    page_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-3', 'real_name': '报工员', 'username': 'reporter'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    page_endpoint = get_route_endpoint(page_router, '/local/work-reports/page')
    page_result = page_endpoint(current=1, size=10, keyword='装配', workOrderId='wo-1')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['processName'], '装配')

    notifications: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    create_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'id': 'wo-1', 'work_order_no': 'WO-001', 'status': 2, 'plan_quantity': 10, 'qualified_quantity': 0, 'applicant': '申请人'}],
        all_queue=[
          [{'user_id': '1'}],
          [{'user_id': 'u-9'}],
        ],
      ),
    )
    create_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      now_str_func=lambda: '2026-03-05 12:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-3', 'real_name': '报工员', 'username': 'reporter'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: notifications.append((args, kwargs)),
    )
    create_endpoint = get_route_endpoint(create_router, '/local/work-reports', 'POST')
    create_result = asyncio.run(
      create_endpoint(JsonRequest({'workOrderId': 'wo-1', 'processName': '装配', 'reportQuantity': 10, 'qualifiedQuantity': 10, 'defectQuantity': 0})),
    )
    self.assertEqual(create_result['code'], 0)
    self.assertEqual(len(notifications), 1)
    self.assertIn('UPDATE work_orders', create_conn.cursor_instance.sql_history[2][0])

  def test_work_inbound_router_page_and_create(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'wi-1',
          'inbound_no': 'WI-001',
          'work_order_id': 'wo-1',
          'work_order_no': 'WO-001',
          'quantity': 10,
          'warehouse_name': '成品仓',
          'operator_name': '仓管员',
          'inbound_time': '2026-03-05 12:00:00',
          'remark': '',
          'create_time': '2026-03-05 12:00:00',
          'product_name': '主机',
          'customer_name': '客户A',
        }]],
      ),
    )
    page_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-4', 'real_name': '仓管员', 'username': 'keeper'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    page_endpoint = get_route_endpoint(page_router, '/local/work-inbounds/page')
    page_result = page_endpoint(current=1, size=10, keyword='WI', workOrderId='wo-1')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['inboundNo'], 'WI-001')

    notifications: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    create_conn = QueueConnection(
      QueueCursor(
        one_queue=[
          {
            'id': 'wo-1',
            'work_order_no': 'WO-001',
            'product_code': 'P-001',
            'product_name': '主机',
            'customer_name': '客户A',
            'qualified_quantity': 10,
            'inbound_quantity': 0,
            'status': 4,
            'applicant': '申请人',
          },
          {'id': 'item-1', 'stock_qty': 5},
          {'qualified_quantity': 10, 'inbound_quantity': 10},
        ],
        all_queue=[
          [{'user_id': '1'}],
          [{'user_id': 'u-9'}],
        ],
      ),
    )
    create_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      now_str_func=lambda: '2026-03-05 12:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-4', 'real_name': '仓管员', 'username': 'keeper'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: notifications.append((args, kwargs)),
    )
    create_endpoint = get_route_endpoint(create_router, '/local/work-inbounds', 'POST')
    create_result = asyncio.run(
      create_endpoint(JsonRequest({'workOrderId': 'wo-1', 'inboundNo': 'WI-001', 'quantity': 10, 'warehouseName': '成品仓'})),
    )
    self.assertEqual(create_result['code'], 0)
    self.assertEqual(len(notifications), 1)
    self.assertIn('UPDATE inventory_items', create_conn.cursor_instance.sql_history[3][0])

  def test_work_order_router_reject_cancel_and_export(self) -> None:
    reject_notifications: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    reject_conn = QueueConnection(
      QueueCursor(
        one_queue=[
          {'status': 1, 'approval_flow_id': 15, 'current_node_index': 1, 'applicant': '申请人', 'work_order_no': 'WO-001'},
          {'id': 31, 'approval_node_name': '生产经理', 'role_id': '', 'approval_ids': 'u-2', 'node_index': 1},
        ],
        all_queue=[
          [{'user_id': '1'}],
          [{'user_id': 'u-9'}],
        ],
      ),
    )
    reject_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: reject_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-2', 'real_name': '审批人', 'username': 'approver'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: reject_notifications.append((args, kwargs)),
    )
    reject_endpoint = get_route_endpoint(reject_router, '/local/work-orders/{work_order_id}/reject', 'POST')
    reject_result = reject_endpoint('wo-1', SimpleNamespace(), '驳回原因')
    self.assertEqual(reject_result['code'], 0)
    self.assertEqual(len(reject_notifications), 1)

    cancel_conn = QueueConnection(QueueCursor(one_queue=[{'status': 1}]))
    cancel_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: cancel_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: {'user_id': 'u-2', 'real_name': '审批人', 'username': 'approver'},
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    cancel_endpoint = get_route_endpoint(cancel_router, '/local/work-orders/{work_order_id}/cancel', 'POST')
    cancel_result = cancel_endpoint('wo-1')
    self.assertEqual(cancel_result['code'], 0)
    self.assertIn('UPDATE work_orders SET status = ?', cancel_conn.cursor_instance.sql_history[1][0])

    export_conn = QueueConnection(
      QueueCursor(
        all_queue=[[{
          'work_order_no': 'WO-001',
          'contract_no': 'CT-001',
          'customer_name': '客户A',
          'product_name': '主机',
          'plan_quantity': 10,
          'reported_quantity': 5,
          'qualified_quantity': 5,
          'inbound_quantity': 3,
          'status': 3,
          'planned_start_date': '2026-03-05',
          'planned_end_date': '2026-03-10',
          'update_time': '2026-03-05 12:00:00',
        }]],
      ),
    )
    export_router = create_work_order_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: export_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      safe_float_func=lambda value, default=0.0: default if value is None else float(value),
      get_current_user_func=lambda request: None,
      export_to_excel_func=lambda headers, rows, sheet: {'headers': headers, 'rows': rows, 'sheet': sheet},
      create_notification_for_users_func=lambda *args, **kwargs: None,
    )
    export_endpoint = get_route_endpoint(export_router, '/local/work-orders/export')
    export_result = export_endpoint(keyword='WO', status=3)
    self.assertEqual(export_result['sheet'], '生产工单列表')
    self.assertEqual(export_result['rows'][0][0], 'WO-001')

  def test_notification_router_page_and_mutations(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[{
          'id': 'n-1',
          'user_id': 'u-1',
          'title': '待审批',
          'content': '请处理',
          'type': 1,
          'biz_type': 'work_order',
          'biz_id': 'wo-1',
          'is_read': 0,
          'create_time': '2026-03-05 12:00:00',
        }]],
      ),
    )
    page_router = create_notification_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      get_current_user_func=lambda request: {'user_id': 'u-1'},
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/local/notifications/page')
    page_result = page_endpoint(SimpleNamespace(query_params={'current': '1', 'size': '20', 'isRead': '0'}))
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['title'], '待审批')

    unread_conn = QueueConnection(QueueCursor(one_queue=[{'cnt': 3}]))
    unread_router = create_notification_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: unread_conn,
      get_current_user_func=lambda request: {'user_id': 'u-1'},
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    unread_endpoint = get_route_endpoint(unread_router, '/local/notifications/unread-count')
    unread_result = unread_endpoint(SimpleNamespace())
    self.assertEqual(unread_result['data']['count'], 3)

    read_conn = QueueConnection(QueueCursor())
    read_router = create_notification_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: read_conn,
      get_current_user_func=lambda request: {'user_id': 'u-1'},
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    read_endpoint = get_route_endpoint(read_router, '/local/notifications/{notification_id}/read', 'PUT')
    read_result = read_endpoint('n-1', SimpleNamespace())
    self.assertEqual(read_result['code'], 0)
    self.assertIn('UPDATE notifications SET is_read = 1', read_conn.cursor_instance.sql_history[0][0])

    delete_conn = QueueConnection(QueueCursor())
    delete_router = create_notification_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: delete_conn,
      get_current_user_func=lambda request: {'user_id': 'u-1'},
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    delete_endpoint = get_route_endpoint(delete_router, '/local/notifications/{notification_id}', 'DELETE')
    delete_result = delete_endpoint('n-1', SimpleNamespace())
    self.assertEqual(delete_result['code'], 0)
    self.assertIn('DELETE FROM notifications', delete_conn.cursor_instance.sql_history[0][0])

  def test_attachment_router_list_upload_and_delete_validation(self) -> None:
    list_conn = QueueConnection(
      QueueCursor(
        all_queue=[[{
          'id': 'a-1',
          'biz_type': 'work_order',
          'biz_id': 'wo-1',
          'file_name': '图纸.pdf',
          'file_size': 128,
          'file_path': '20260305/a-1.pdf',
          'upload_by': 'Alice',
          'upload_time': '2026-03-05 12:00:00',
        }]],
      ),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
      uploads_dir = Path(tmpdir)
      list_router = create_attachment_router(
        ok_func=_ok_wrapper,
        fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
        get_conn_func=lambda: list_conn,
        get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': 'Alice'},
        now_str_func=lambda: '2026-03-05 12:00:00',
        uploads_dir=uploads_dir,
      )
      list_endpoint = get_route_endpoint(list_router, '/local/attachments/list')
      list_result = list_endpoint(SimpleNamespace(query_params={'bizType': 'work_order', 'bizId': 'wo-1'}))
      self.assertEqual(list_result['code'], 0)
      self.assertEqual(list_result['data'][0]['fileName'], '图纸.pdf')

      upload_conn = QueueConnection(QueueCursor())
      upload_router = create_attachment_router(
        ok_func=_ok_wrapper,
        fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
        get_conn_func=lambda: upload_conn,
        get_current_user_func=lambda request: {'user_id': 'u-1', 'real_name': 'Alice'},
        now_str_func=lambda: '2026-03-05 12:00:00',
        uploads_dir=uploads_dir,
      )
      upload_endpoint = get_route_endpoint(upload_router, '/local/attachments/upload', 'POST')
      upload_result = asyncio.run(
        upload_endpoint(UploadRequest({}), FakeUploadFile('图纸.pdf', b'pdf-data'), 'work_order', 'wo-1'),
      )
      self.assertEqual(upload_result['code'], 0)
      self.assertIn('INSERT INTO attachments', upload_conn.cursor_instance.sql_history[0][0])

      bad_upload_result = asyncio.run(
        upload_endpoint(UploadRequest({}), FakeUploadFile('', b''), 'work_order', 'wo-1'),
      )
      self.assertEqual(bad_upload_result['code'], 400)

      delete_conn = QueueConnection(QueueCursor(one_queue=[None]))
      delete_router = create_attachment_router(
        ok_func=_ok_wrapper,
        fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
        get_conn_func=lambda: delete_conn,
        get_current_user_func=lambda request: None,
        now_str_func=lambda: '2026-03-05 12:00:00',
        uploads_dir=uploads_dir,
      )
      delete_endpoint = get_route_endpoint(delete_router, '/local/attachments/{attachment_id}', 'DELETE')
      delete_result = delete_endpoint('missing-id')
      self.assertEqual(delete_result['code'], 400)

  def test_basic_info_router_page_and_save_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 8,
              'name': '喷涂',
              'type': 13,
              'parent_id': None,
              'create_time': '2026-03-01 00:00:00',
              'update_time': '2026-03-02 00:00:00',
            },
          ],
        ],
      ),
    )
    page_router = create_basic_info_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/manage/api/basicInformation/page')
    page_result = page_endpoint(current=1, size=10, type=13, keyWord='喷')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['name'], '喷涂')

    save_conn = QueueConnection(QueueCursor())
    save_router = create_basic_info_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: save_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    save_endpoint = get_route_endpoint(save_router, '/manage/api/basicInformation/save', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'name': '', 'type': 0})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_scan_binding_router_page_and_save_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 1,
              'scan_asset_number': 'SA-001',
              'identifier': 'QR-001',
              'process_id': 8,
              'create_time': '2026-03-01 00:00:00',
              'update_time': '2026-03-02 00:00:00',
            },
          ],
          [{'id': 8, 'name': '喷涂'}],
        ],
      ),
    )
    page_router = create_scan_binding_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/manage/api/scanBindingProcess/page')
    page_result = page_endpoint(current=1, size=10, keyWord='SA')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['processName'], '喷涂')

    save_conn = QueueConnection(QueueCursor())
    save_router = create_scan_binding_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: save_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    save_endpoint = get_route_endpoint(save_router, '/manage/api/scanBindingProcess/save', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'scanAssetNumber': '', 'identifier': '', 'processId': 0})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_code_rule_router_page_and_save_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 'rule-1',
              'type': 1,
              'prefix': 'PO',
              'rule_name': '生产订单规则',
              'is_enable': 1,
              'remark': '',
              'create_time': '2026-03-01 00:00:00',
              'update_time': '2026-03-02 00:00:00',
            },
          ],
        ],
      ),
    )
    page_router = create_code_rule_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    page_endpoint = get_route_endpoint(page_router, '/manage/api/codeRule/page')
    page_result = page_endpoint(current=1, size=10, keyword='生产')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['prefix'], 'PO')

    save_conn = QueueConnection(QueueCursor())
    save_router = create_code_rule_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: save_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    save_endpoint = get_route_endpoint(save_router, '/manage/api/codeRule/save', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'type': 0, 'prefix': '', 'ruleName': ''})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_sys_log_router_page_and_delete_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 1,
              'type': 1,
              'content': '导出报表',
              'sys_log_id': 'log-1',
              'creator': 'admin',
              'create_by': 'u-1',
              'real_name': '管理员',
              'create_time': '2026-03-01 00:00:00',
              'update_time': '2026-03-02 00:00:00',
              'tenant_code': 'LOCAL',
            },
          ],
        ],
      ),
    )
    page_router = create_sys_log_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
    )
    page_endpoint = get_route_endpoint(page_router, '/admin/api/sysLogUser')
    page_result = page_endpoint(current=1, size=10, content='导出')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['realName'], '管理员')

    delete_router = create_sys_log_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: QueueConnection(QueueCursor()),
    )
    delete_endpoint = get_route_endpoint(delete_router, '/admin/api/sysLogUser', 'DELETE')
    bad_delete_result = delete_endpoint(SimpleNamespace(query_params=SimpleNamespace(getlist=lambda key: [])))
    self.assertEqual(bad_delete_result['code'], 400)

  def test_sys_backup_router_page_and_trigger_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[
          {
            'id': 'bak-1',
            'name': 'local-backup-20260301.sql',
            'type': 1,
            'status': 1,
            'create_name': '系统管理员',
            'create_time': '2026-03-01 00:00:00',
          },
        ]],
      ),
    )
    router = create_sys_backup_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
    )
    page_endpoint = get_route_endpoint(router, '/manage/api/sysBakInfo/page')
    page_result = page_endpoint(current=1, size=10, name='local')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['type'], '手动备份')

    trigger_endpoint = get_route_endpoint(router, '/manage/api/sysBakInfo/backup')
    bad_trigger_result = trigger_endpoint('')
    self.assertEqual(bad_trigger_result['code'], 400)

  def test_approval_flow_router_page_and_save_validation(self) -> None:
    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[[
          {
            'id': 1,
            'approval_flow_name': '标准审批',
            'process_library_id': '1',
            'approval_type': 1,
            'status': 1,
            'remarks': '',
            'creator': '系统管理员',
            'create_by': '1',
            'create_time': '2026-03-01 00:00:00',
            'update_time': '2026-03-02 00:00:00',
          },
        ]],
      ),
    )
    router = create_approval_flow_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      get_process_library_records_func=lambda: [{'id': '1', 'processName': '标准工序'}],
    )
    page_endpoint = get_route_endpoint(router, '/manage/api/approvalFlow/page')
    page_result = page_endpoint(current=1, size=10, keyword='标准')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['processLibraryName'], '标准工序')

    save_endpoint = get_route_endpoint(router, '/manage/api/approvalFlow/save', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'approvalFlowName': ''})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_approval_flow_result_router_page_and_save_validation(self) -> None:
    result_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'id': 1,
              'order_id': 'o-1',
              'result_type': 2,
              'order_scheduling_id': 'os-1',
              'order_name': '排程单1',
              'product_name': '产品A',
              'process_library_id': '1',
              'approval_flow_id': 1,
              'process_people': 'u-1',
              'approval_status': 3,
              'approval_remarks': '',
              'creator': '系统管理员',
              'create_time': '2026-03-01 00:00:00',
            },
          ],
          [{'id': 1, 'approval_flow_name': '标准审批'}],
          [{'user_id': 'u-1', 'real_name': 'Alice', 'username': 'alice'}],
        ],
      ),
    )
    router = create_approval_flow_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: result_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      get_process_library_records_func=lambda: [{'id': '1', 'processName': '标准工序'}],
    )
    page_endpoint = get_route_endpoint(router, '/manage/api/approvalFlowResult/page')
    page_result = page_endpoint(current=1, size=10, keyword='排程')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['approvalFlowName'], '标准审批')

    save_endpoint = get_route_endpoint(router, '/manage/api/approvalFlowResult/saveApprovalResult', 'POST')
    bad_save_result = asyncio.run(save_endpoint(JsonRequest({'orderSchedulingId': ''})))
    self.assertEqual(bad_save_result['code'], 400)

  def test_system_admin_router_menu_routes(self) -> None:
    role_rows = [{'menu_id': '1000'}, {'menu_id': '2200'}]
    conn = FakeConnection(rows=role_rows)

    router = create_system_admin_router(
      ok_func=_ok_wrapper,
      get_conn_func=lambda: conn,
      menu_tree_func=lambda: [{'id': '1000', 'children': []}],
    )

    get_tree = get_route_endpoint(router, '/admin/menu/tree')
    get_role_menu = get_route_endpoint(router, '/admin/menu/tree/{role_id}')

    tree_result = get_tree()
    self.assertEqual(tree_result['code'], 0)
    self.assertEqual(len(tree_result['data']), 1)

    role_result = get_role_menu('role-admin')
    self.assertEqual(role_result['code'], 0)
    self.assertEqual(role_result['data'], ['1000', '2200'])
    self.assertTrue(conn.closed)
    self.assertIn('SELECT menu_id FROM role_menus', conn.cursor_instance.executed_sql)
    self.assertEqual(conn.cursor_instance.executed_params, ('role-admin',))

  def test_system_admin_router_empty_role_menu_routes(self) -> None:
    conn = FakeConnection(rows=[])
    router = create_system_admin_router(
      ok_func=_ok_wrapper,
      get_conn_func=lambda: conn,
      menu_tree_func=lambda: [],
    )
    get_role_menu = get_route_endpoint(router, '/admin/menu/tree/{role_id}')
    result = get_role_menu('role-empty')
    self.assertEqual(result['code'], 0)
    self.assertEqual(result['data'], [])
    self.assertEqual(conn.cursor_instance.executed_params, ('role-empty',))

  def test_dept_read_router_page_and_tree(self) -> None:
    conn = ScriptedDeptConnection()
    router = create_dept_read_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: conn,
      build_dept_tree_func=lambda include_users=True: [{'deptId': '1', 'name': '总部', 'children': []}],
    )

    get_tree = get_route_endpoint(router, '/admin/dept/tree')
    get_user_tree = get_route_endpoint(router, '/admin/dept/user-tree')
    get_page = get_route_endpoint(router, '/admin/dept/page')

    tree_result = get_tree()
    user_tree_result = get_user_tree()
    self.assertEqual(tree_result['code'], 0)
    self.assertEqual(user_tree_result['code'], 0)
    self.assertEqual(tree_result['data'][0]['deptId'], '1')

    request = SimpleNamespace(query_params={'current': '1', 'size': '10', 'name': '部', 'parentId': '1'})
    page_result = get_page(request)
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['total'], 2)
    self.assertEqual(len(page_result['data']['records']), 2)
    self.assertEqual(page_result['data']['records'][0]['parentName'], '总部')
    self.assertTrue(conn.closed)
    self.assertIn('SELECT COUNT(1) AS cnt FROM depts', conn.cursor_instance.sql_history[0][0])

  def test_dept_read_router_detail_by_name_not_found(self) -> None:
    conn = QueueConnection(QueueCursor(one_queue=[None]))
    router = create_dept_read_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: conn,
      build_dept_tree_func=lambda include_users=True: [],
    )
    get_detail = get_route_endpoint(router, '/admin/dept/details/{dept_name}')
    result = get_detail('不存在部门')
    self.assertEqual(result['code'], 404)
    self.assertEqual(result['msg'], '部门不存在')

  def test_dept_read_router_detail_by_id(self) -> None:
    dept_row = {
      'dept_id': '10',
      'name': '研发部',
      'parent_id': '1',
      'sort_order': 1,
      'enabled': 1,
      'create_time': '2026-03-01 00:00:00',
      'update_time': '2026-03-02 00:00:00',
    }
    user_row = {
      'user_id': 'u-1',
      'username': 'alice',
      'real_name': 'Alice',
      'phone': '',
      'email': '',
      'enabled': 1,
      'dept_id': '10',
    }
    conn = QueueConnection(
      QueueCursor(
        one_queue=[dept_row, {'cnt': 1}],
        all_queue=[
          [{'dept_id': '1', 'name': '总部'}, {'dept_id': '10', 'name': '研发部'}],
          [user_row],
        ],
      ),
    )
    router = create_dept_read_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: conn,
      build_dept_tree_func=lambda include_users=True: [],
    )
    get_detail = get_route_endpoint(router, '/admin/dept/{dept_id}')
    result = get_detail('10')
    self.assertEqual(result['code'], 0)
    self.assertEqual(result['data']['deptId'], '10')
    self.assertEqual(result['data']['parentName'], '总部')
    self.assertEqual(result['data']['userCount'], 1)

  def test_dept_write_router_validation_paths(self) -> None:
    router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: None,
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )

    delete_dept = get_route_endpoint(router, '/admin/dept/{dept_id}', 'DELETE')
    result = delete_dept('1')
    self.assertEqual(result['code'], 400)
    self.assertEqual(result['msg'], '默认根部门不可删除')

    update_users = get_route_endpoint(router, '/admin/dept/updateUserDeptId', 'POST')
    bad_request = JsonRequest({'deptId': '10', 'userIdList': 'not-list'})
    result2 = asyncio.run(update_users(bad_request))
    self.assertEqual(result2['code'], 400)
    self.assertEqual(result2['msg'], 'userIdList格式错误')

  def test_role_router_list_and_delete_validation(self) -> None:
    role_rows = [
      {
        'role_id': '1',
        'role_name': '管理员',
        'role_code': 'admin',
        'role_desc': '系统管理员',
        'del_flag': '0',
        'create_time': '2026-03-01 00:00:00',
        'update_time': '2026-03-02 00:00:00',
      },
    ]
    list_conn = QueueConnection(QueueCursor(all_queue=[role_rows]))
    router = create_role_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: list_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    get_list = get_route_endpoint(router, '/admin/role/list')
    list_result = get_list()
    self.assertEqual(list_result['code'], 0)
    self.assertEqual(list_result['data'][0]['roleName'], '管理员')

    delete_role = get_route_endpoint(router, '/admin/role/{role_id}', 'DELETE')
    delete_result = delete_role('1')
    self.assertEqual(delete_result['code'], 400)
    self.assertEqual(delete_result['msg'], '系统管理员角色不可删除')

  def test_role_router_page_detail_and_menu_update(self) -> None:
    role_row = {
      'role_id': '2',
      'role_name': '普通用户',
      'role_code': 'user',
      'role_desc': '普通角色',
      'del_flag': '0',
      'create_time': '2026-03-01 00:00:00',
      'update_time': '2026-03-02 00:00:00',
    }
    page_conn = QueueConnection(QueueCursor(one_queue=[{'cnt': 1}], all_queue=[[role_row]]))
    page_router = create_role_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    get_page = get_route_endpoint(page_router, '/admin/role/page')
    page_result = get_page(current=1, size=10, roleName='普通')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['records'][0]['roleId'], '2')

    detail_conn = QueueConnection(QueueCursor(one_queue=[role_row]))
    detail_router = create_role_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: detail_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    get_detail = get_route_endpoint(detail_router, '/admin/role/{role_id}')
    detail_result = get_detail('2')
    self.assertEqual(detail_result['code'], 0)
    self.assertEqual(detail_result['data']['roleCode'], 'user')

    menu_conn = QueueConnection(QueueCursor(one_queue=[{'role_id': '2'}]))
    menu_router = create_role_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: menu_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    update_role_menu = get_route_endpoint(menu_router, '/admin/role/menu', 'PUT')
    menu_result = asyncio.run(update_role_menu(JsonRequest({'roleId': '2', 'menuIds': '1000,2200'})))
    self.assertEqual(menu_result['code'], 0)
    self.assertEqual(menu_conn.commit_count, 1)
    self.assertIn('DELETE FROM role_menus WHERE role_id = ?', menu_conn.cursor_instance.sql_history[1][0])
    self.assertEqual(
      menu_conn.cursor_instance.executemany_history[0][1],
      [('2', '1000'), ('2', '2200')],
    )

  def test_role_router_write_and_lookup_success_paths(self) -> None:
    create_conn = QueueConnection(QueueCursor(one_queue=[None]))
    create_router = create_role_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    create_role = get_route_endpoint(create_router, '/admin/role', 'POST')
    create_result = asyncio.run(
      create_role(JsonRequest({'roleName': '采购员', 'roleCode': 'buyer', 'roleDesc': '采购角色'})),
    )
    self.assertEqual(create_result['code'], 0)
    self.assertEqual(create_conn.commit_count, 1)
    self.assertIn('INSERT INTO roles', create_conn.cursor_instance.sql_history[1][0])

    update_conn = QueueConnection(QueueCursor(one_queue=[{'role_id': '3'}, None]))
    update_router = create_role_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: update_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    update_role = get_route_endpoint(update_router, '/admin/role', 'PUT')
    update_result = asyncio.run(
      update_role(
        JsonRequest({'roleId': '3', 'roleName': '采购主管', 'roleCode': 'buyer-lead', 'roleDesc': '采购主管角色'}),
      ),
    )
    self.assertEqual(update_result['code'], 0)
    self.assertEqual(update_conn.commit_count, 1)
    self.assertIn('UPDATE roles', update_conn.cursor_instance.sql_history[2][0])

    lookup_conn = QueueConnection(QueueCursor(all_queue=[[{'user_id': 'u-1'}, {'user_id': 'u-2'}]]))
    lookup_router = create_role_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: lookup_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
    )
    get_user_ids = get_route_endpoint(lookup_router, '/admin/role/getUserByRoleId')
    lookup_result = get_user_ids(roleId='3')
    self.assertEqual(lookup_result['code'], 0)
    self.assertEqual(lookup_result['data'], ['u-1', 'u-2'])

  def test_dept_write_router_additional_paths(self) -> None:
    create_conn = QueueConnection(QueueCursor(one_queue=[None]))
    create_router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )
    create_endpoint = get_route_endpoint(create_router, '/admin/dept', 'POST')
    invalid_parent_result = asyncio.run(
      create_endpoint(JsonRequest({'sysDept': {'name': '研发部', 'parentId': '99', 'sortOrder': 1, 'enabled': 1}})),
    )
    self.assertEqual(invalid_parent_result['code'], 400)
    self.assertEqual(invalid_parent_result['msg'], '上级部门不存在')

    update_router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: QueueConnection(QueueCursor()),
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )
    update_endpoint = get_route_endpoint(update_router, '/admin/dept', 'PUT')
    self_parent_result = asyncio.run(
      update_endpoint(JsonRequest({'sysDept': {'deptId': '10', 'name': '研发部', 'parentId': '10'}})),
    )
    self.assertEqual(self_parent_result['code'], 400)
    self.assertEqual(self_parent_result['msg'], '上级部门不能是自己')

    delete_conn = QueueConnection(QueueCursor(one_queue=[{'dept_id': '10'}, {'cnt': 1}, {'cnt': 0}]))
    delete_router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: delete_conn,
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )
    delete_endpoint = get_route_endpoint(delete_router, '/admin/dept/{dept_id}', 'DELETE')
    delete_result = delete_endpoint('10')
    self.assertEqual(delete_result['code'], 400)
    self.assertEqual(delete_result['msg'], '请先移除子组织和成员后再删除')

    enabled_conn = QueueConnection(QueueCursor())
    enabled_router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: enabled_conn,
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )
    toggle_enabled = get_route_endpoint(enabled_router, '/admin/dept/enabled')
    enabled_result = toggle_enabled(id='10', type=1)
    self.assertEqual(enabled_result['code'], 0)
    self.assertEqual(enabled_conn.commit_count, 1)
    self.assertIn('UPDATE depts SET enabled = ?, update_time = ? WHERE dept_id = ?', enabled_conn.cursor_instance.sql_history[0][0])

  def test_dept_write_router_successful_mutations(self) -> None:
    create_conn = QueueConnection(QueueCursor(one_queue=[{'dept_id': '1'}, None]))
    create_router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )
    create_endpoint = get_route_endpoint(create_router, '/admin/dept', 'POST')
    create_result = asyncio.run(
      create_endpoint(
        JsonRequest(
          {
            'sysDept': {'name': '新部门', 'parentId': '1', 'sortOrder': 2, 'enabled': 1},
            'userIdList': ['u-1'],
          },
        ),
      ),
    )
    self.assertEqual(create_result['code'], 0)
    self.assertEqual(create_conn.commit_count, 1)
    self.assertIn('INSERT INTO depts', create_conn.cursor_instance.sql_history[2][0])

    update_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'dept_id': '10'}, {'dept_id': '1'}, None],
        all_queue=[[{'dept_id': '10', 'parent_id': '1'}]],
      ),
    )
    update_router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: update_conn,
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )
    update_endpoint = get_route_endpoint(update_router, '/admin/dept', 'PUT')
    update_result = asyncio.run(
      update_endpoint(
        JsonRequest(
          {
            'sysDept': {'deptId': '10', 'name': '研发二部', 'parentId': '1', 'sortOrder': 3, 'enabled': 1},
            'userIdList': ['u-2'],
          },
        ),
      ),
    )
    self.assertEqual(update_result['code'], 0)
    self.assertEqual(update_conn.commit_count, 1)
    self.assertIn('UPDATE depts', update_conn.cursor_instance.sql_history[4][0])

    delete_conn = QueueConnection(QueueCursor(one_queue=[{'dept_id': '10'}, {'cnt': 0}, {'cnt': 0}]))
    delete_router = create_dept_write_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: delete_conn,
      safe_int_func=lambda value, default=0: default if value is None else int(value),
      now_str_func=lambda: '2026-03-05 00:00:00',
      collect_descendant_ids_func=lambda dept_id, rows: set(),
    )
    delete_endpoint = get_route_endpoint(delete_router, '/admin/dept/{dept_id}', 'DELETE')
    delete_result = delete_endpoint('10')
    self.assertEqual(delete_result['code'], 0)
    self.assertEqual(delete_conn.commit_count, 1)
    self.assertIn('DELETE FROM depts', delete_conn.cursor_instance.sql_history[3][0])

  def test_user_router_info_and_page(self) -> None:
    info_conn = QueueConnection(QueueCursor(one_queue=[{'name': '研发部'}]))
    router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: info_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: {
        'user_id': 'u-1',
        'username': 'alice',
        'phone': '13800000000',
        'email': 'alice@example.com',
        'dept_id': '10',
        'real_name': 'Alice',
        'role_id': '2',
      },
    )
    get_info = get_route_endpoint(router, '/admin/user/info')
    info_result = get_info(SimpleNamespace())
    self.assertEqual(info_result['code'], 0)
    self.assertEqual(info_result['data']['deptName'], '研发部')
    self.assertEqual(info_result['data']['sysUser']['userId'], 'u-1')

    page_conn = QueueConnection(
      QueueCursor(
        one_queue=[{'cnt': 1}],
        all_queue=[
          [
            {
              'user_id': 'u-2',
              'username': 'bob',
              'real_name': 'Bob',
              'phone': '',
              'email': 'bob@example.com',
              'enabled': 1,
              'role_id': '2',
              'update_time': '2026-03-05 12:00:00',
              'role_name': '普通用户',
            },
          ],
        ],
      ),
    )
    page_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: page_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    get_page = get_route_endpoint(page_router, '/admin/user/page')
    page_result = get_page(current=1, size=10, username='bo')
    self.assertEqual(page_result['code'], 0)
    self.assertEqual(page_result['data']['total'], 1)
    self.assertEqual(page_result['data']['records'][0]['username'], 'bob')

  def test_user_router_mutation_and_lookup_paths(self) -> None:
    all_user_conn = QueueConnection(
      QueueCursor(
        all_queue=[[{'user_id': 'u-1', 'username': 'admin', 'real_name': '管理员'}]],
      ),
    )
    all_user_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: all_user_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    get_all_users = get_route_endpoint(all_user_router, '/admin/user/getAllUser')
    all_users_result = get_all_users()
    self.assertEqual(all_users_result['code'], 0)
    self.assertEqual(all_users_result['data'][0]['username'], 'admin')

    detail_conn = QueueConnection(QueueCursor(one_queue=[None]))
    detail_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: detail_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    get_user_detail = get_route_endpoint(detail_router, '/admin/user/{user_id}')
    detail_result = get_user_detail('missing-user')
    self.assertEqual(detail_result['code'], 404)
    self.assertEqual(detail_result['msg'], '用户不存在')

    create_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: QueueConnection(QueueCursor()),
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    create_user = get_route_endpoint(create_router, '/admin/user', 'POST')
    bad_create_result = asyncio.run(create_user(JsonRequest({'username': '', 'realName': ''})))
    self.assertEqual(bad_create_result['code'], 400)

    update_conn = QueueConnection(QueueCursor(one_queue=[None]))
    update_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: update_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    update_user = get_route_endpoint(update_router, '/admin/user', 'PUT')
    update_result = asyncio.run(update_user(JsonRequest({'userId': 'missing-user'})))
    self.assertEqual(update_result['code'], 404)
    self.assertEqual(update_result['msg'], '用户不存在')

    update_pwd = get_route_endpoint(update_router, '/admin/user/updatePwd', 'PUT')
    bad_pwd_result = asyncio.run(update_pwd(JsonRequest({'userId': '', 'password': ''})))
    self.assertEqual(bad_pwd_result['code'], 400)
    self.assertEqual(bad_pwd_result['msg'], '参数不完整')

    delete_user = get_route_endpoint(update_router, '/admin/user/{user_id}', 'DELETE')
    delete_result = delete_user('1')
    self.assertEqual(delete_result['code'], 400)
    self.assertEqual(delete_result['msg'], '默认管理员不可删除')

    reset_pwd = get_route_endpoint(update_router, '/admin/user/resetPwd')
    reset_result = reset_pwd()
    self.assertEqual(reset_result['code'], 400)
    self.assertEqual(reset_result['msg'], '用户ID不能为空')

    enabled_conn = QueueConnection(QueueCursor())
    enabled_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: enabled_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    toggle_enabled = get_route_endpoint(enabled_router, '/admin/user/enabled')
    enabled_result = toggle_enabled(id='u-1', enabled=1)
    self.assertEqual(enabled_result['code'], 0)
    self.assertEqual(enabled_conn.commit_count, 1)
    self.assertIn('UPDATE users SET enabled = ?, update_time = ? WHERE user_id = ?', enabled_conn.cursor_instance.sql_history[0][0])

  def test_user_router_successful_write_paths(self) -> None:
    create_conn = QueueConnection(QueueCursor())
    create_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: create_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    create_user = get_route_endpoint(create_router, '/admin/user', 'POST')
    create_result = asyncio.run(
      create_user(
        JsonRequest(
          {
            'username': 'carol',
            'realName': 'Carol',
            'password': '123456',
            'phone': '13900000000',
            'email': 'carol@example.com',
            'role': ['2'],
          },
        ),
      ),
    )
    self.assertEqual(create_result['code'], 0)
    self.assertEqual(create_conn.commit_count, 1)
    self.assertIn('INSERT INTO users', create_conn.cursor_instance.sql_history[0][0])

    update_conn = QueueConnection(QueueCursor(one_queue=[{'user_id': 'u-2'}]))
    update_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: update_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    update_user = get_route_endpoint(update_router, '/admin/user', 'PUT')
    update_result = asyncio.run(
      update_user(
        JsonRequest(
          {
            'userId': 'u-2',
            'realName': 'Bob Lee',
            'phone': '13700000000',
            'email': 'bob.lee@example.com',
            'role': ['3'],
          },
        ),
      ),
    )
    self.assertEqual(update_result['code'], 0)
    self.assertEqual(update_conn.commit_count, 1)
    self.assertIn('UPDATE users SET', update_conn.cursor_instance.sql_history[1][0])

    reset_conn = QueueConnection(QueueCursor())
    reset_router = create_user_router(
      ok_func=_ok_wrapper,
      fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
      get_conn_func=lambda: reset_conn,
      now_str_func=lambda: '2026-03-05 00:00:00',
      hash_password_func=lambda text: f'hashed::{text}',
      get_current_user_func=lambda request: None,
    )
    reset_pwd = get_route_endpoint(reset_router, '/admin/user/resetPwd/{id}')
    reset_result = reset_pwd('u-2')
    self.assertEqual(reset_result['code'], 0)
    self.assertEqual(reset_conn.commit_count, 1)
    self.assertIn('UPDATE users SET password = ?, update_time = ? WHERE user_id = ?', reset_conn.cursor_instance.sql_history[0][0])


if __name__ == '__main__':
  unittest.main()
