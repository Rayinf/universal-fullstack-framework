from __future__ import annotations

from typing import Any

from app.modules.system_admin.scaffold_menu_registry import scaffolded_backend_menu_registry


BUCKET_PARENT_MENU_IDS = {
  'system': '2000',
  'sales': '3000',
  'production': '4000',
}


def _clone_menu_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
  cloned: list[dict[str, Any]] = []
  for node in nodes:
    cloned_node = dict(node)
    children = node.get('children') or []
    cloned_node['children'] = _clone_menu_nodes(children)
    cloned.append(cloned_node)
  return cloned


def _find_menu_node_by_id(nodes: list[dict[str, Any]], menu_id: str) -> dict[str, Any] | None:
  for node in nodes:
    if str(node.get('id')) == menu_id:
      return node
    children = node.get('children') or []
    found = _find_menu_node_by_id(children, menu_id)
    if found:
      return found
  return None


def _collect_existing_ids(nodes: list[dict[str, Any]]) -> set[str]:
  existing_ids: set[str] = set()
  for node in nodes:
    existing_ids.add(str(node.get('id')))
    children = node.get('children') or []
    existing_ids.update(_collect_existing_ids(children))
  return existing_ids


def _merge_scaffolded_menu_tree(base_tree: list[dict[str, Any]]) -> list[dict[str, Any]]:
  merged_tree = _clone_menu_nodes(base_tree)
  existing_ids = _collect_existing_ids(merged_tree)

  for bucket, bucket_nodes in scaffolded_backend_menu_registry.items():
    if not bucket_nodes:
      continue

    target_list: list[dict[str, Any]]
    if bucket == 'root':
      target_list = merged_tree
      parent_id = '0'
    else:
      parent_menu_id = BUCKET_PARENT_MENU_IDS.get(bucket)
      if not parent_menu_id:
        continue
      parent_node = _find_menu_node_by_id(merged_tree, parent_menu_id)
      if not parent_node:
        continue
      children = parent_node.get('children')
      if not isinstance(children, list):
        children = []
        parent_node['children'] = children
      target_list = children
      parent_id = parent_menu_id

    for node in bucket_nodes:
      node_id = str(node.get('id', '')).strip()
      if not node_id or node_id in existing_ids:
        continue

      cloned_node = dict(node)
      cloned_node['id'] = node_id
      cloned_node['parentId'] = str(cloned_node.get('parentId') or parent_id)
      cloned_node['children'] = _clone_menu_nodes(cloned_node.get('children') or [])
      target_list.append(cloned_node)
      existing_ids.add(node_id)

  return merged_tree


def menu_tree() -> list[dict[str, Any]]:
  base_tree = [
    {
      'id': '1000',
      'parentId': '0',
      'name': '首页',
      'label': '首页',
      'path': '/',
      'icon': 'HomeFilled',
      'permission': 'FRAMEWORK-HOME',
      'type': '0',
      'children': [],
    },
    {
      'id': '1100',
      'parentId': '0',
      'name': '本地基础CRUD',
      'label': '本地基础CRUD',
      'path': '/system/basic-crud',
      'icon': 'List',
      'permission': 'SRS-FUNC-00011-LOCAL-CRUD',
      'type': '0',
      'children': [],
    },
    {
      'id': '1110',
      'parentId': '0',
      'name': '项目管理示例',
      'label': '项目管理示例',
      'path': '/system/project-demo',
      'icon': 'FolderOpened',
      'permission': 'SRS-FUNC-00011-LOCAL-PROJECT',
      'type': '0',
      'children': [],
    },
    {
      'id': '1120',
      'parentId': '0',
      'name': '采购订单示例',
      'label': '采购订单示例',
      'path': '/system/purchase-demo',
      'icon': 'ShoppingCart',
      'permission': 'SRS-FUNC-00011-LOCAL-PURCHASE',
      'type': '0',
      'children': [],
    },
    {
      'id': '1130',
      'parentId': '0',
      'name': '库存管理示例',
      'label': '库存管理示例',
      'path': '/system/inventory-demo',
      'icon': 'DataBoard',
      'permission': 'SRS-FUNC-00011-LOCAL-INVENTORY',
      'type': '0',
      'children': [],
    },
    {
      'id': '2000',
      'parentId': '0',
      'name': '系统管理',
      'label': '系统管理',
      'path': '/system',
      'icon': 'Setting',
      'permission': 'SRS-FUNC-00011',
      'type': '0',
      'children': [
        {
          'id': '2200',
          'parentId': '2000',
          'name': '组织架构管理',
          'label': '组织架构管理',
          'path': '/system/dept-management',
          'icon': 'OfficeBuilding',
          'permission': 'SRS-FUNC-00011-1',
          'type': '0',
          'children': [],
        },
        {
          'id': '2300',
          'parentId': '2000',
          'name': '账户管理',
          'label': '账户管理',
          'path': '/system/account-management',
          'icon': 'User',
          'permission': 'SRS-FUNC-00011-2-3-4',
          'type': '0',
          'children': [],
        },
        {
          'id': '2400',
          'parentId': '2000',
          'name': '客户管理',
          'label': '客户管理',
          'path': '/system/customers',
          'icon': 'Avatar',
          'permission': 'SRS-FUNC-00011-14',
          'type': '0',
          'children': [],
        },
        {
          'id': '2500',
          'parentId': '2000',
          'name': '用户角色管理',
          'label': '用户角色管理',
          'path': '/system/role',
          'icon': 'Key',
          'permission': 'SRS-FUNC-00011-5',
          'type': '0',
          'children': [],
        },
        {
          'id': '2600',
          'parentId': '2000',
          'name': '工位与设备管理',
          'label': '工位与设备管理',
          'path': '/system/workstation',
          'icon': 'Cpu',
          'permission': 'SRS-FUNC-00011-6',
          'type': '0',
          'children': [
            {
              'id': '2610',
              'parentId': '2600',
              'name': '工位信息管理',
              'label': '工位信息管理',
              'path': '/system/workstation/info',
              'icon': 'Setting',
              'permission': 'SRS-FUNC-00011-6.1',
              'type': '0',
              'children': [],
            },
            {
              'id': '2620',
              'parentId': '2600',
              'name': '设备基础信息管理',
              'label': '设备基础信息管理',
              'path': '/system/workstation/equipment',
              'icon': 'Setting',
              'permission': 'SRS-FUNC-00011-6.2',
              'type': '0',
              'children': [],
            },
          ],
        },
        {
          'id': '2700',
          'parentId': '2000',
          'name': '参数与字典',
          'label': '参数与字典',
          'path': '/system/param',
          'icon': 'Notebook',
          'permission': 'SRS-FUNC-00011-7',
          'type': '0',
          'children': [
            {
              'id': '2710',
              'parentId': '2700',
              'name': '参数管理',
              'label': '参数管理',
              'path': '/system/param/manage',
              'icon': 'List',
              'permission': 'SRS-FUNC-00011-7.1',
              'type': '0',
              'children': [],
            },
            {
              'id': '2720',
              'parentId': '2700',
              'name': '编码规则配置',
              'label': '编码规则配置',
              'path': '/system/param/code',
              'icon': 'List',
              'permission': 'SRS-FUNC-00011-7.2',
              'type': '0',
              'children': [],
            },
          ],
        },
        {
          'id': '2800',
          'parentId': '2000',
          'name': '业务相关审批规则',
          'label': '业务相关审批规则',
          'path': '/system/approval',
          'icon': 'Stamp',
          'permission': 'SRS-FUNC-00011-8',
          'type': '0',
          'children': [],
        },
        {
          'id': '2810',
          'parentId': '2000',
          'name': '系统日志管理',
          'label': '系统日志管理',
          'path': '/system/operation-log',
          'icon': 'Monitor',
          'permission': 'SRS-FUNC-00011-9',
          'type': '0',
          'children': [],
        },
        {
          'id': '2820',
          'parentId': '2000',
          'name': '用户日志管理',
          'label': '用户日志管理',
          'path': '/system/user-log',
          'icon': 'Reading',
          'permission': 'SRS-FUNC-00011-10',
          'type': '0',
          'children': [],
        },
        {
          'id': '2830',
          'parentId': '2000',
          'name': '数据与系统备份',
          'label': '数据与系统备份',
          'path': '/system/backup',
          'icon': 'Coin',
          'permission': 'SRS-FUNC-00011-13',
          'type': '0',
          'children': [],
        },
        {
          'id': '2900',
          'parentId': '2000',
          'name': '系统基础配置',
          'label': '系统基础配置',
          'path': '/system/system-config',
          'icon': 'Operation',
          'permission': 'SRS-FUNC-00011-11',
          'type': '0',
          'children': [],
        },
      ],
    },
    {
      'id': '3000',
      'parentId': '0',
      'name': '销售管理',
      'label': '销售管理',
      'path': '/sales',
      'icon': 'DataLine',
      'permission': 'SRS-FUNC-00011-LOCAL-SALES',
      'type': '0',
      'children': [
        {
          'id': '2910',
          'parentId': '3000',
          'name': '产品目录管理',
          'label': '产品目录管理',
          'path': '/sales/product-catalog',
          'icon': 'Goods',
          'permission': 'SRS-FUNC-00011-LOCAL-PRODUCT',
          'type': '0',
          'children': [],
        },
        {
          'id': '2920',
          'parentId': '3000',
          'name': '报价单管理',
          'label': '报价单管理',
          'path': '/sales/quotation',
          'icon': 'Money',
          'permission': 'SRS-FUNC-00011-LOCAL-QUOTATION',
          'type': '0',
          'children': [],
        },
        {
          'id': '2930',
          'parentId': '3000',
          'name': '合同管理',
          'label': '合同管理',
          'path': '/sales/contracts',
          'icon': 'Collection',
          'permission': 'SRS-FUNC-00011-LOCAL-CONTRACT',
          'type': '0',
          'children': [],
        },
        {
          'id': '2940',
          'parentId': '3000',
          'name': '回款跟踪',
          'label': '回款跟踪',
          'path': '/sales/payments',
          'icon': 'Wallet',
          'permission': 'SRS-FUNC-00011-LOCAL-PAYMENT',
          'type': '0',
          'children': [],
        },
        {
          'id': '2950',
          'parentId': '3000',
          'name': '佣金计算',
          'label': '佣金计算',
          'path': '/sales/commissions',
          'icon': 'TrendCharts',
          'permission': 'SRS-FUNC-00011-LOCAL-COMMISSION',
          'type': '0',
          'children': [],
        },
        {
          'id': '2960',
          'parentId': '3000',
          'name': '合同业务看板',
          'label': '合同业务看板',
          'path': '/sales/contract-dashboard',
          'icon': 'DataAnalysis',
          'permission': 'SRS-FUNC-00011-LOCAL-CONTRACT-DASHBOARD',
          'type': '0',
          'children': [],
        },
      ],
    },
    {
      'id': '4000',
      'parentId': '0',
      'name': '生产执行',
      'label': '生产执行',
      'path': '/production',
      'icon': 'Files',
      'permission': 'SRS-FUNC-00011-LOCAL-PRODUCTION',
      'type': '0',
      'children': [
        {
          'id': '2970',
          'parentId': '4000',
          'name': '生产工单管理',
          'label': '生产工单管理',
          'path': '/production/work-orders',
          'icon': 'Tickets',
          'permission': 'SRS-FUNC-00011-LOCAL-WORK-ORDER',
          'type': '0',
          'children': [],
        },
        {
          'id': '2980',
          'parentId': '4000',
          'name': '工序报工',
          'label': '工序报工',
          'path': '/production/work-reports',
          'icon': 'Clock',
          'permission': 'SRS-FUNC-00011-LOCAL-WORK-REPORT',
          'type': '0',
          'children': [],
        },
        {
          'id': '2990',
          'parentId': '4000',
          'name': '完工入库',
          'label': '完工入库',
          'path': '/production/work-inbounds',
          'icon': 'SoldOut',
          'permission': 'SRS-FUNC-00011-LOCAL-WORK-INBOUND',
          'type': '0',
          'children': [],
        },
        {
          'id': '2995',
          'parentId': '4000',
          'name': '生产工单看板',
          'label': '生产工单看板',
          'path': '/production/work-order-dashboard',
          'icon': 'Odometer',
          'permission': 'SRS-FUNC-00011-LOCAL-WORK-ORDER-DASHBOARD',
          'type': '0',
          'children': [],
        },
      ],
    },
  ]
  return _merge_scaffolded_menu_tree(base_tree)

def flatten_menu_ids(nodes: list[dict[str, Any]]) -> list[str]:
  ids: list[str] = []
  for node in nodes:
    ids.append(str(node['id']))
    children = node.get('children') or []
    if children:
      ids.extend(flatten_menu_ids(children))
  return ids
