from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / 'scripts' / 'scaffold_fullstack_module.py'


class FullstackScaffoldTestCase(unittest.TestCase):
  def test_scaffold_fullstack_module_generates_expected_files(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      src_root = Path(temp_dir) / 'src'
      backend_root = Path(temp_dir) / 'backend'
      backend_output_root = backend_root / 'app' / 'modules'
      backend_bootstrap_root = backend_root / 'app' / 'bootstrap'

      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'quality_report',
          '--tag',
          '质检报告',
          '--api-base-path',
          '/manage/api/qualityReport',
          '--table-name',
          'quality_report_records',
          '--menu-parent',
          'production',
          '--route-path',
          '/production/quality-report',
          '--route-name',
          'production-quality-report',
          '--function-code',
          'SRS-FUNC-QUALITY-REPORT',
          '--menu-icon',
          'DataAnalysis',
          '--with-store',
          '--src-root',
          str(src_root),
          '--backend-root',
          str(backend_root),
          '--backend-output-root',
          str(backend_output_root),
          '--backend-bootstrap-root',
          str(backend_bootstrap_root),
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertEqual(result.returncode, 0, msg=result.stderr)

      module_root = backend_output_root / 'quality_report'
      self.assertTrue((module_root / 'router.py').exists())
      self.assertTrue((module_root / 'routes' / 'quality_report_routes.py').exists())
      self.assertTrue((module_root / 'services' / 'quality_report_query_service.py').exists())
      self.assertTrue((module_root / 'services' / 'quality_report_command_service.py').exists())
      self.assertTrue((module_root / 'repositories' / 'quality_report_repo.py').exists())

      self.assertTrue((src_root / 'types' / 'production' / 'qualityReport.ts').exists())
      self.assertTrue((src_root / 'api' / 'production' / 'qualityReport.ts').exists())
      self.assertTrue((src_root / 'views' / 'production' / 'QualityReportManagement.vue').exists())
      self.assertTrue((src_root / 'stores' / 'production' / 'qualityReport.ts').exists())
      self.assertTrue((src_root / 'router' / 'scaffoldedRoutes.ts').exists())
      self.assertTrue((src_root / 'config' / 'scaffoldMenuRegistry.ts').exists())
      self.assertTrue((backend_bootstrap_root / 'scaffold_router_registry.py').exists())
      self.assertTrue(
        (backend_root / 'app' / 'modules' / 'system_admin' / 'scaffold_menu_registry.py').exists(),
      )

      route_registry_text = (src_root / 'router' / 'scaffoldedRoutes.ts').read_text(
        encoding='utf-8',
      )
      menu_registry_text = (src_root / 'config' / 'scaffoldMenuRegistry.ts').read_text(
        encoding='utf-8',
      )
      backend_menu_registry_text = (
        backend_root / 'app' / 'modules' / 'system_admin' / 'scaffold_menu_registry.py'
      ).read_text(encoding='utf-8')
      router_registry_text = (backend_bootstrap_root / 'scaffold_router_registry.py').read_text(
        encoding='utf-8',
      )
      api_text = (src_root / 'api' / 'production' / 'qualityReport.ts').read_text(
        encoding='utf-8',
      )
      repo_text = (module_root / 'repositories' / 'quality_report_repo.py').read_text(
        encoding='utf-8',
      )

      self.assertIn("path: '/production/quality-report'", route_registry_text)
      self.assertIn("name: 'production-quality-report'", route_registry_text)
      self.assertIn("functionCode: 'SRS-FUNC-QUALITY-REPORT'", route_registry_text)
      self.assertIn("id: 'production-quality-report'", menu_registry_text)
      self.assertIn("icon: 'DataAnalysis'", menu_registry_text)
      self.assertIn("functionCode: 'SRS-FUNC-QUALITY-REPORT'", menu_registry_text)
      self.assertIn("'id': 'production-quality-report'", backend_menu_registry_text)
      self.assertIn("'path': '/production/quality-report'", backend_menu_registry_text)
      self.assertIn("'permission': 'SRS-FUNC-QUALITY-REPORT'", backend_menu_registry_text)
      self.assertIn("'module': 'app.modules.quality_report.router'", router_registry_text)
      self.assertIn("'factory': 'create_quality_report_router'", router_registry_text)
      self.assertIn('/manage/api/qualityReport/page', api_text)
      self.assertIn('quality_report_records', repo_text)

      compile_result = subprocess.run(
        [
          sys.executable,
          '-m',
          'py_compile',
          *[str(path) for path in sorted(module_root.rglob('*.py'))],
          str(SCRIPT_PATH),
        ],
        capture_output=True,
        text=True,
        check=False,
      )
      self.assertEqual(compile_result.returncode, 0, msg=compile_result.stderr)

  def test_scaffold_fullstack_module_stops_before_partial_write_on_conflict(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      src_root = Path(temp_dir) / 'src'
      backend_root = Path(temp_dir) / 'backend'
      backend_output_root = backend_root / 'app' / 'modules'
      backend_bootstrap_root = backend_root / 'app' / 'bootstrap'
      existing_api_file = src_root / 'api' / 'system' / 'qualityReport.ts'
      existing_api_file.parent.mkdir(parents=True, exist_ok=True)
      existing_api_file.write_text('// existing', encoding='utf-8')

      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'quality_report',
          '--src-root',
          str(src_root),
          '--backend-root',
          str(backend_root),
          '--backend-output-root',
          str(backend_output_root),
          '--backend-bootstrap-root',
          str(backend_bootstrap_root),
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertNotEqual(result.returncode, 0)
      self.assertIn('目标文件已存在', result.stderr)
      self.assertFalse((backend_output_root / 'quality_report').exists())
      self.assertFalse((backend_bootstrap_root / 'scaffold_router_registry.py').exists())
      self.assertFalse(
        (backend_root / 'app' / 'modules' / 'system_admin' / 'scaffold_menu_registry.py').exists(),
      )


if __name__ == '__main__':
  unittest.main()
