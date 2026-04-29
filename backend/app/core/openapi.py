from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

DOC_TAGS = [
  {'name': '系统与认证', 'description': '健康检查、登录与令牌刷新相关接口。'},
  {'name': '系统配置', 'description': '系统名称、公司信息等基础配置接口。'},
  {'name': '菜单与权限', 'description': '菜单树与角色菜单授权接口。'},
  {'name': '组织与用户', 'description': '部门、角色、用户等组织权限接口。'},
  {'name': '客户管理', 'description': '客户资料维护相关接口。'},
  {'name': '工位与工艺', 'description': '工位、工艺库、设备等基础数据接口。'},
  {'name': '基础参数', 'description': '基础信息、扫码绑定、编码规则等参数接口。'},
  {'name': '日志与备份', 'description': '用户日志、操作日志、系统备份接口。'},
  {'name': '审批流', 'description': '审批流程、审批结果相关接口。'},
  {'name': '本地示例-CRUD', 'description': '本地 CRUD 示例接口。'},
  {'name': '本地示例-项目管理', 'description': '项目管理示例接口。'},
  {'name': '本地示例-采购管理', 'description': '采购订单示例接口。'},
  {'name': '本地示例-库存管理', 'description': '库存主数据与流水示例接口。'},
  {'name': '本地示例-生产工单', 'description': '生产工单、报工与完工入库示例接口。'},
  {'name': '其他接口', 'description': '未归类接口。'},
]

DOC_TAG_PREFIXES: list[tuple[str, str]] = [
  ('/auth/', '系统与认证'),
  ('/health', '系统与认证'),
  ('/manage/api/systemConfig', '系统配置'),
  ('/admin/menu', '菜单与权限'),
  ('/admin/dept', '组织与用户'),
  ('/admin/role', '组织与用户'),
  ('/admin/user', '组织与用户'),
  ('/manage/api/customers', '客户管理'),
  ('/manage/api/workstation', '工位与工艺'),
  ('/manage/api/processLibrary', '工位与工艺'),
  ('/manage/api/deviceInfo', '工位与工艺'),
  ('/manage/api/basicInformation', '基础参数'),
  ('/manage/api/scanBindingProcess', '基础参数'),
  ('/manage/api/codeRule', '基础参数'),
  ('/admin/api/sysLogUser', '日志与备份'),
  ('/manage/api/sysLog', '日志与备份'),
  ('/manage/api/sysBakInfo', '日志与备份'),
  ('/manage/api/approvalFlow', '审批流'),
  ('/manage/api/approvalFlowResult', '审批流'),
  ('/local/crud', '本地示例-CRUD'),
  ('/local/projects', '本地示例-项目管理'),
  ('/local/purchase-orders', '本地示例-采购管理'),
  ('/local/inventory', '本地示例-库存管理'),
  ('/local/work-orders', '本地示例-生产工单'),
  ('/local/work-reports', '本地示例-生产工单'),
  ('/local/work-inbounds', '本地示例-生产工单'),
]

DOC_EXACT_SUMMARIES: dict[tuple[str, str], str] = {
  ('/health', 'get'): '健康检查',
  ('/auth/oauth2/token', 'post'): '账号登录',
  ('/auth/oauth2/refresh', 'post'): '刷新访问令牌',
  ('/admin/user/info', 'get'): '获取当前登录用户信息',
  ('/admin/menu/tree', 'get'): '获取当前用户菜单树',
  ('/manage/api/systemConfig/getSystemDefaultData', 'get'): '获取系统默认配置',
  ('/manage/api/systemConfig/update', 'put'): '更新系统配置',
  ('/manage/api/systemConfig/updateSystemDefaultData', 'post'): '更新系统默认配置',
  ('/local/crud/page', 'get'): '分页查询基础 CRUD 数据',
  ('/local/crud', 'post'): '新增基础 CRUD 数据',
  ('/local/crud/{item_id}', 'put'): '更新基础 CRUD 数据',
  ('/local/crud/{item_id}', 'delete'): '删除基础 CRUD 数据',
  ('/local/projects/page', 'get'): '分页查询项目数据',
  ('/local/projects', 'post'): '新增项目',
  ('/local/projects/{project_id}', 'put'): '更新项目',
  ('/local/projects/{project_id}', 'delete'): '删除项目',
  ('/local/purchase-orders/page', 'get'): '分页查询采购订单',
  ('/local/purchase-orders', 'post'): '新增采购订单',
  ('/local/purchase-orders/{order_id}', 'put'): '更新采购订单',
  ('/local/purchase-orders/{order_id}/submit', 'post'): '提交采购订单',
  ('/local/purchase-orders/{order_id}/approve', 'post'): '审批通过采购订单',
  ('/local/purchase-orders/{order_id}/cancel', 'post'): '作废采购订单',
  ('/local/purchase-orders/{order_id}/approval-status', 'get'): '查询采购订单审批状态',
  ('/local/purchase-orders/{order_id}', 'delete'): '删除采购订单',
  ('/local/inventory/items/page', 'get'): '分页查询库存主数据',
  ('/local/inventory/items', 'post'): '新增库存物料',
  ('/local/inventory/items/{item_id}', 'put'): '更新库存物料',
  ('/local/inventory/items/{item_id}', 'delete'): '删除库存物料',
  ('/local/inventory/summary', 'get'): '查询库存汇总',
  ('/local/inventory/transactions/page', 'get'): '分页查询库存流水',
  ('/local/inventory/transactions', 'post'): '新增库存流水',
  ('/local/work-orders/page', 'get'): '分页查询生产工单',
  ('/local/work-orders/export', 'get'): '导出生产工单',
  ('/local/work-orders', 'post'): '新增生产工单',
  ('/local/work-orders/{work_order_id}', 'put'): '更新生产工单',
  ('/local/work-orders/{work_order_id}/submit', 'post'): '提交生产工单审批',
  ('/local/work-orders/{work_order_id}/approve', 'post'): '审批通过生产工单',
  ('/local/work-orders/{work_order_id}/reject', 'post'): '驳回生产工单',
  ('/local/work-orders/{work_order_id}/cancel', 'post'): '作废生产工单',
  ('/local/work-orders/{work_order_id}/approval-status', 'get'): '查询生产工单审批状态',
  ('/local/work-orders/dashboard', 'get'): '获取生产工单看板数据',
  ('/local/work-reports/page', 'get'): '分页查询工序报工记录',
  ('/local/work-reports/export', 'get'): '导出工序报工记录',
  ('/local/work-reports', 'post'): '新增工序报工',
  ('/local/work-inbounds/page', 'get'): '分页查询完工入库记录',
  ('/local/work-inbounds/export', 'get'): '导出完工入库记录',
  ('/local/work-inbounds', 'post'): '新增完工入库',
}


def _resolve_doc_tag(path: str) -> str:
  for prefix, tag_name in DOC_TAG_PREFIXES:
    if path.startswith(prefix):
      return tag_name
  return '其他接口'


def _build_doc_summary(path: str, method: str, tag_name: str) -> str:
  exact_summary = DOC_EXACT_SUMMARIES.get((path, method))
  if exact_summary:
    return exact_summary

  target = tag_name.replace('本地示例-', '')
  leaf = path.rstrip('/').split('/')[-1]

  if method == 'get':
    if leaf == 'page':
      return f'分页查询{target}'
    if leaf == 'list':
      return f'获取{target}列表'
    if leaf == 'tree' or leaf.endswith('tree'):
      return f'获取{target}树'
    if '{' in leaf and '}' in leaf:
      return f'获取{target}详情'
    return f'查询{target}'

  if method == 'post':
    if leaf == 'save':
      return f'新增{target}'
    if leaf == 'update':
      return f'更新{target}'
    if leaf == 'submit':
      return f'提交{target}'
    if leaf == 'approve':
      return f'审批{target}'
    if leaf == 'cancel':
      return f'作废{target}'
    return f'提交{target}操作'

  if method == 'put':
    return f'更新{target}'
  if method == 'delete':
    return f'删除{target}'
  if method == 'patch':
    return f'部分更新{target}'
  return f'{target}接口'


def create_custom_openapi(app: FastAPI) -> Callable[[], dict[str, Any]]:
  def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
      return app.openapi_schema

    openapi_schema = get_openapi(
      title=app.title,
      version=app.version,
      description=app.description,
      routes=app.routes,
    )

    for path, methods in openapi_schema.get('paths', {}).items():
      tag_name = _resolve_doc_tag(path)
      for method, operation in methods.items():
        if method not in {'get', 'post', 'put', 'delete', 'patch'}:
          continue
        if not isinstance(operation, dict):
          continue

        summary = _build_doc_summary(path, method, tag_name)
        operation['summary'] = summary
        if not operation.get('tags'):
          operation['tags'] = [tag_name]
        if not operation.get('description'):
          operation['description'] = (
            f'【接口说明】{summary}。\n'
            '【返回说明】统一返回 `{code, msg, data}`，其中 `code=0` 表示成功。'
          )

    app.openapi_schema = openapi_schema
    return app.openapi_schema

  return custom_openapi
