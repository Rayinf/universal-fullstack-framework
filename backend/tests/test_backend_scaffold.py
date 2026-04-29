from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = BACKEND_ROOT / 'scripts' / 'scaffold_backend_module.py'


class BackendScaffoldTestCase(unittest.TestCase):
  def test_scaffold_backend_module_generates_expected_files(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      output_root = Path(temp_dir) / 'modules'
      bootstrap_root = Path(temp_dir) / 'bootstrap'
      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'demo_quality',
          '--tag',
          '质检模块',
          '--resource-path',
          '/manage/api/demoQuality',
          '--table-name',
          'demo_quality_records',
          '--output-root',
          str(output_root),
          '--bootstrap-root',
          str(bootstrap_root),
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertEqual(result.returncode, 0, msg=result.stderr)
      module_root = output_root / 'demo_quality'
      self.assertTrue((module_root / 'router.py').exists())
      self.assertTrue((module_root / 'routes' / 'demo_quality_routes.py').exists())
      self.assertTrue((module_root / 'services' / 'demo_quality_query_service.py').exists())
      self.assertTrue((module_root / 'services' / 'demo_quality_command_service.py').exists())
      self.assertTrue((module_root / 'repositories' / 'demo_quality_repo.py').exists())
      self.assertTrue((bootstrap_root / 'scaffold_router_registry.py').exists())

      router_text = (module_root / 'router.py').read_text(encoding='utf-8')
      routes_text = (module_root / 'routes' / 'demo_quality_routes.py').read_text(encoding='utf-8')
      deps_text = (module_root / 'deps.py').read_text(encoding='utf-8')
      repo_text = (module_root / 'repositories' / 'demo_quality_repo.py').read_text(encoding='utf-8')
      router_registry_text = (bootstrap_root / 'scaffold_router_registry.py').read_text(
        encoding='utf-8',
      )

      self.assertIn('create_demo_quality_router', router_text)
      self.assertIn('app.modules.demo_quality.deps', router_text)
      self.assertIn('DemoQualityRouterDeps', deps_text)
      self.assertIn('/manage/api/demoQuality/page', routes_text)
      self.assertIn('/manage/api/demoQuality', routes_text)
      self.assertIn('demo_quality_records', repo_text)
      self.assertIn("'module': 'app.modules.demo_quality.router'", router_registry_text)
      self.assertIn("'factory': 'create_demo_quality_router'", router_registry_text)

      compile_result = subprocess.run(
        [
          sys.executable,
          '-m',
          'py_compile',
          *[str(path) for path in sorted(module_root.rglob('*.py'))],
        ],
        capture_output=True,
        text=True,
        check=False,
      )
      self.assertEqual(compile_result.returncode, 0, msg=compile_result.stderr)

  def test_scaffold_backend_module_rejects_existing_target(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      output_root = Path(temp_dir) / 'modules'
      bootstrap_root = Path(temp_dir) / 'bootstrap'
      (output_root / 'demo_quality').mkdir(parents=True, exist_ok=True)

      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'demo_quality',
          '--output-root',
          str(output_root),
          '--bootstrap-root',
          str(bootstrap_root),
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertNotEqual(result.returncode, 0)
      self.assertIn('目标模块目录已存在', result.stderr)

  def test_scaffold_backend_module_supports_skip_router_registration(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      output_root = Path(temp_dir) / 'modules'
      bootstrap_root = Path(temp_dir) / 'bootstrap'

      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'demo_quality',
          '--output-root',
          str(output_root),
          '--bootstrap-root',
          str(bootstrap_root),
          '--skip-router-registration',
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertEqual(result.returncode, 0, msg=result.stderr)
      self.assertFalse((bootstrap_root / 'scaffold_router_registry.py').exists())


if __name__ == '__main__':
  unittest.main()
