from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
  sys.path.insert(0, str(BACKEND_ROOT))

from app.bootstrap.router_registry import register_scaffolded_routers


class FakeApp:
  def __init__(self) -> None:
    self.routers: list[object] = []

  def include_router(self, router: object) -> None:
    self.routers.append(router)


class RouterRegistryTestCase(unittest.TestCase):
  def test_register_scaffolded_routers_imports_and_mounts_registry_entries(self) -> None:
    captured_calls: list[dict[str, object]] = []

    def fake_factory(**kwargs):
      captured_calls.append(kwargs)
      return {'router': 'demo'}

    fake_module = SimpleNamespace(create_demo_quality_router=fake_factory)
    app = FakeApp()

    with patch(
      'app.bootstrap.router_registry.scaffolded_router_registry',
      [{'module': 'app.modules.demo_quality.router', 'factory': 'create_demo_quality_router'}],
    ), patch('app.bootstrap.router_registry.import_module', return_value=fake_module) as import_mock:
      register_scaffolded_routers(
        app,
        ok_func=lambda data, msg='success': {'code': 0, 'msg': msg, 'data': data},
        fail_func=lambda msg, code: {'code': code, 'msg': msg, 'data': None},
        get_conn_func=lambda: object(),
      )

    import_mock.assert_called_once_with('app.modules.demo_quality.router')
    self.assertEqual(len(app.routers), 1)
    self.assertEqual(app.routers[0], {'router': 'demo'})
    self.assertEqual(len(captured_calls), 1)
    self.assertIn('ok_func', captured_calls[0])
    self.assertIn('fail_func', captured_calls[0])
    self.assertIn('get_conn_func', captured_calls[0])


if __name__ == '__main__':
  unittest.main()
