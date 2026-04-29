from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / 'scripts' / 'scaffold_frontend_module.py'


class FrontendScaffoldTestCase(unittest.TestCase):
  def test_scaffold_frontend_module_generates_expected_files(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      src_root = Path(temp_dir) / 'src'
      backend_root = Path(temp_dir) / 'backend'
      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'quality_report',
          '--tag',
          '质检报告',
          '--api-base-path',
          '/manage/api/qualityReport',
          '--src-root',
          str(src_root),
          '--backend-root',
          str(backend_root),
          '--with-store',
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertEqual(result.returncode, 0, msg=result.stderr)
      self.assertTrue((src_root / 'types' / 'system' / 'qualityReport.ts').exists())
      self.assertTrue((src_root / 'api' / 'system' / 'qualityReport.ts').exists())
      self.assertTrue((src_root / 'views' / 'system-admin' / 'QualityReportManagement.vue').exists())
      self.assertTrue((src_root / 'stores' / 'system' / 'qualityReport.ts').exists())
      self.assertTrue((src_root / 'router' / 'scaffoldedRoutes.ts').exists())
      self.assertTrue((src_root / 'config' / 'scaffoldMenuRegistry.ts').exists())
      self.assertTrue(
        (
          backend_root / 'app' / 'modules' / 'system_admin' / 'scaffold_menu_registry.py'
        ).exists(),
      )

      types_text = (src_root / 'types' / 'system' / 'qualityReport.ts').read_text(encoding='utf-8')
      api_text = (src_root / 'api' / 'system' / 'qualityReport.ts').read_text(encoding='utf-8')
      view_text = (
        src_root / 'views' / 'system-admin' / 'QualityReportManagement.vue'
      ).read_text(encoding='utf-8')
      store_text = (src_root / 'stores' / 'system' / 'qualityReport.ts').read_text(encoding='utf-8')
      route_registry_text = (src_root / 'router' / 'scaffoldedRoutes.ts').read_text(
        encoding='utf-8',
      )
      menu_registry_text = (src_root / 'config' / 'scaffoldMenuRegistry.ts').read_text(
        encoding='utf-8',
      )
      backend_menu_registry_text = (
        backend_root / 'app' / 'modules' / 'system_admin' / 'scaffold_menu_registry.py'
      ).read_text(encoding='utf-8')

      self.assertIn('export interface QualityReportRecord', types_text)
      self.assertIn('/manage/api/qualityReport/page', api_text)
      self.assertIn("import { useQualityReportStore } from '@/stores/system/qualityReport'", view_text)
      self.assertIn("import { usePageQuery } from '@/composables/usePageQuery'", view_text)
      self.assertIn("defineStore('qualityReport'", store_text)
      self.assertIn("path: '/system/quality-report'", route_registry_text)
      self.assertIn("name: 'system-quality-report'", route_registry_text)
      self.assertIn("import('@/views/system-admin/QualityReportManagement.vue')", route_registry_text)
      self.assertIn("id: 'system-quality-report'", menu_registry_text)
      self.assertIn("title: '质检报告管理'", menu_registry_text)
      self.assertIn("path: '/system/quality-report'", menu_registry_text)
      self.assertIn("'id': 'system-quality-report'", backend_menu_registry_text)
      self.assertIn("'label': '质检报告管理'", backend_menu_registry_text)
      self.assertIn("'path': '/system/quality-report'", backend_menu_registry_text)
      self.assertNotIn('__MODULE_', api_text)
      self.assertNotIn('__MODULE_', view_text)

  def test_scaffold_frontend_module_rejects_existing_target(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      src_root = Path(temp_dir) / 'src'
      backend_root = Path(temp_dir) / 'backend'
      target_file = src_root / 'api' / 'system' / 'qualityReport.ts'
      target_file.parent.mkdir(parents=True, exist_ok=True)
      target_file.write_text('// existing', encoding='utf-8')

      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'quality_report',
          '--src-root',
          str(src_root),
          '--backend-root',
          str(backend_root),
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertNotEqual(result.returncode, 0)
      self.assertIn('目标文件已存在', result.stderr)

  def test_scaffold_frontend_module_supports_skip_registration_flags(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
      src_root = Path(temp_dir) / 'src'
      backend_root = Path(temp_dir) / 'backend'
      result = subprocess.run(
        [
          sys.executable,
          str(SCRIPT_PATH),
          'quality_report',
          '--src-root',
          str(src_root),
          '--backend-root',
          str(backend_root),
          '--skip-route-registration',
          '--skip-menu-registration',
          '--skip-backend-menu-registration',
        ],
        capture_output=True,
        text=True,
        check=False,
      )

      self.assertEqual(result.returncode, 0, msg=result.stderr)
      self.assertFalse((src_root / 'router' / 'scaffoldedRoutes.ts').exists())
      self.assertFalse((src_root / 'config' / 'scaffoldMenuRegistry.ts').exists())
      self.assertFalse(
        (
          backend_root / 'app' / 'modules' / 'system_admin' / 'scaffold_menu_registry.py'
        ).exists(),
      )


if __name__ == '__main__':
  unittest.main()
