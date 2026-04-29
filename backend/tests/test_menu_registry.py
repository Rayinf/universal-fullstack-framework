from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
  sys.path.insert(0, str(BACKEND_ROOT))

from app.modules.system_admin.menu import flatten_menu_ids, menu_tree


class MenuRegistryTestCase(unittest.TestCase):
  def test_menu_tree_merges_scaffolded_entries(self) -> None:
    registry = {
      'root': [
        {
          'id': 'custom-root-dashboard',
          'name': '自定义首页看板',
          'label': '自定义首页看板',
          'path': '/custom/dashboard',
          'icon': 'DataAnalysis',
          'permission': 'CUSTOM-DASHBOARD',
          'type': '0',
          'children': [],
        },
      ],
      'system': [
        {
          'id': 'system-quality-report',
          'name': '质检报告管理',
          'label': '质检报告管理',
          'path': '/system/quality-report',
          'icon': 'Document',
          'permission': 'SRS-FUNC-QUALITY-REPORT',
          'type': '0',
          'children': [],
        },
      ],
      'sales': [],
      'production': [],
    }

    with patch('app.modules.system_admin.menu.scaffolded_backend_menu_registry', registry):
      merged_tree = menu_tree()

    root_node = next((node for node in merged_tree if node['id'] == 'custom-root-dashboard'), None)
    self.assertIsNotNone(root_node)
    self.assertEqual(root_node['parentId'], '0')

    system_node = next(node for node in merged_tree if node['id'] == '2000')
    system_child = next(
      (child for child in system_node['children'] if child['id'] == 'system-quality-report'),
      None,
    )
    self.assertIsNotNone(system_child)
    self.assertEqual(system_child['parentId'], '2000')

    merged_ids = flatten_menu_ids(merged_tree)
    self.assertIn('custom-root-dashboard', merged_ids)
    self.assertIn('system-quality-report', merged_ids)


if __name__ == '__main__':
  unittest.main()
