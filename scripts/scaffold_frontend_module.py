from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_ROOT = REPO_ROOT / 'scaffolds' / 'frontend_module'
DEFAULT_SRC_ROOT = REPO_ROOT / 'src'
DEFAULT_BACKEND_ROOT = REPO_ROOT / 'backend'
MODULE_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')
PASCAL_NAME_PATTERN = re.compile(r'^[A-Z][A-Za-z0-9]*$')
MENU_PARENT_PREFIX_MAP = {
  'root': '',
  'system': '/system',
  'sales': '/sales',
  'production': '/production',
}
DEFAULT_MENU_ICON = 'Document'
ROUTE_REGISTRY_RELATIVE_PATH = Path('router') / 'scaffoldedRoutes.ts'
MENU_REGISTRY_RELATIVE_PATH = Path('config') / 'scaffoldMenuRegistry.ts'
BACKEND_MENU_REGISTRY_RELATIVE_PATH = (
  Path('app') / 'modules' / 'system_admin' / 'scaffold_menu_registry.py'
)
ROUTE_REGISTRY_MARKER = '  // __SCAFFOLD_ROUTE_ENTRIES__'
MENU_REGISTRY_MARKERS = {
  'root': '    // __SCAFFOLD_ROOT_MENU_ENTRIES__',
  'system': '    // __SCAFFOLD_SYSTEM_MENU_ENTRIES__',
  'sales': '    // __SCAFFOLD_SALES_MENU_ENTRIES__',
  'production': '    // __SCAFFOLD_PRODUCTION_MENU_ENTRIES__',
}
BACKEND_MENU_REGISTRY_MARKERS = {
  'root': '    # __SCAFFOLD_BACKEND_ROOT_MENU_ENTRIES__',
  'system': '    # __SCAFFOLD_BACKEND_SYSTEM_MENU_ENTRIES__',
  'sales': '    # __SCAFFOLD_BACKEND_SALES_MENU_ENTRIES__',
  'production': '    # __SCAFFOLD_BACKEND_PRODUCTION_MENU_ENTRIES__',
}
ROUTE_REGISTRY_TEMPLATE = """import type { RouteRecordRaw } from 'vue-router'

export const scaffoldedRoutes: RouteRecordRaw[] = [
  // __SCAFFOLD_ROUTE_ENTRIES__
]
"""
MENU_REGISTRY_TEMPLATE = """type ScaffoldMenuItem = {
  id: string
  title: string
  path?: string
  icon?: string
  children?: ScaffoldMenuItem[]
  functionCode?: string
  hidden?: boolean
  roles?: string[]
}

export type ScaffoldMenuBucket = 'root' | 'system' | 'sales' | 'production'

export const scaffoldedMenuRegistry: Record<ScaffoldMenuBucket, ScaffoldMenuItem[]> = {
  root: [
    // __SCAFFOLD_ROOT_MENU_ENTRIES__
  ],
  system: [
    // __SCAFFOLD_SYSTEM_MENU_ENTRIES__
  ],
  sales: [
    // __SCAFFOLD_SALES_MENU_ENTRIES__
  ],
  production: [
    // __SCAFFOLD_PRODUCTION_MENU_ENTRIES__
  ],
}
"""
BACKEND_MENU_REGISTRY_TEMPLATE = """from __future__ import annotations

from typing import Any


scaffolded_backend_menu_registry: dict[str, list[dict[str, Any]]] = {
  'root': [
    # __SCAFFOLD_BACKEND_ROOT_MENU_ENTRIES__
  ],
  'system': [
    # __SCAFFOLD_BACKEND_SYSTEM_MENU_ENTRIES__
  ],
  'sales': [
    # __SCAFFOLD_BACKEND_SALES_MENU_ENTRIES__
  ],
  'production': [
    # __SCAFFOLD_BACKEND_PRODUCTION_MENU_ENTRIES__
  ],
}
"""


@dataclass(frozen=True)
class FrontendScaffoldContext:
  module_name: str
  module_pascal: str
  module_camel: str
  module_kebab: str
  tag: str
  page_title: str
  page_description: str
  api_base_path: str
  api_dir: str
  type_dir: str
  view_dir: str
  store_dir: str
  view_name: str
  with_store: bool
  menu_parent: str
  route_path: str
  route_name: str
  menu_id: str
  menu_title: str
  menu_icon: str
  function_code: str | None
  register_route: bool
  register_menu: bool
  backend_menu_id: str
  register_backend_menu: bool


def snake_to_pascal(name: str) -> str:
  return ''.join(part.capitalize() for part in name.split('_') if part)


def snake_to_camel(name: str) -> str:
  pascal_name = snake_to_pascal(name)
  if not pascal_name:
    return ''
  return f'{pascal_name[0].lower()}{pascal_name[1:]}'


def snake_to_kebab(name: str) -> str:
  return '-'.join(part for part in name.split('_') if part)


def escape_ts_string(value: str) -> str:
  return value.replace('\\', '\\\\').replace("'", "\\'")


def validate_module_name(module_name: str) -> None:
  if not MODULE_NAME_PATTERN.match(module_name):
    raise ValueError('module_name 必须是 snake_case，且只能包含小写字母、数字、下划线')


def validate_pascal_name(name: str, label: str) -> None:
  if not PASCAL_NAME_PATTERN.match(name):
    raise ValueError(f'{label} 必须是 PascalCase，例如 QualityReport')


def validate_menu_parent(menu_parent: str) -> None:
  if menu_parent not in MENU_PARENT_PREFIX_MAP:
    supported = ', '.join(MENU_PARENT_PREFIX_MAP.keys())
    raise ValueError(f'menu_parent 仅支持: {supported}')


def normalize_relative_dir(dir_name: str) -> str:
  return dir_name.strip().strip('/')


def normalize_api_base_path(api_base_path: str) -> str:
  normalized = api_base_path.strip() or '/'
  if not normalized.startswith('/'):
    normalized = f'/{normalized}'
  if len(normalized) > 1 and normalized.endswith('/'):
    normalized = normalized.rstrip('/')
  return normalized


def normalize_route_path(route_path: str) -> str:
  normalized = route_path.strip() or '/'
  if not normalized.startswith('/'):
    normalized = f'/{normalized}'
  if len(normalized) > 1 and normalized.endswith('/'):
    normalized = normalized.rstrip('/')
  return normalized


def normalize_required_text(value: str, label: str) -> str:
  normalized = value.strip()
  if not normalized:
    raise ValueError(f'{label} 不能为空')
  return normalized


def normalize_optional_text(value: str | None) -> str | None:
  if value is None:
    return None
  normalized = value.strip()
  return normalized or None


def default_api_base_path(module_name: str) -> str:
  return f'/manage/api/{snake_to_camel(module_name)}'


def default_route_path(module_name: str, menu_parent: str) -> str:
  prefix = MENU_PARENT_PREFIX_MAP[menu_parent]
  suffix = snake_to_kebab(module_name)
  if not prefix:
    return f'/{suffix}'
  return f'{prefix}/{suffix}'


def default_route_name(module_name: str, menu_parent: str) -> str:
  suffix = snake_to_kebab(module_name)
  if menu_parent == 'root':
    return suffix
  return f'{menu_parent}-{suffix}'


def default_menu_id(route_name: str) -> str:
  return route_name


def default_backend_menu_id(route_name: str) -> str:
  return route_name


def build_view_import_path(view_dir: str, view_name: str) -> str:
  if view_dir:
    return f"@/views/{view_dir}/{view_name}.vue"
  return f"@/views/{view_name}.vue"


def validate_route_matches_menu_parent(route_path: str, menu_parent: str) -> None:
  prefix = MENU_PARENT_PREFIX_MAP[menu_parent]
  if not prefix:
    return
  if route_path == prefix or route_path.startswith(f'{prefix}/'):
    return
  raise ValueError(f'route_path 必须位于 {prefix} 路径前缀下，当前为: {route_path}')


def build_context(
  *,
  module_name: str,
  tag: str,
  api_base_path: str,
  api_dir: str,
  type_dir: str,
  view_dir: str,
  store_dir: str,
  file_stem: str,
  entity_name: str,
  view_name: str,
  description: str | None,
  with_store: bool,
  menu_parent: str,
  route_path: str,
  route_name: str,
  menu_id: str,
  menu_title: str | None,
  menu_icon: str,
  function_code: str | None,
  register_route: bool,
  register_menu: bool,
  backend_menu_id: str,
  register_backend_menu: bool,
) -> FrontendScaffoldContext:
  validate_module_name(module_name)
  validate_pascal_name(entity_name, 'entity_name')
  validate_pascal_name(view_name, 'view_name')
  validate_menu_parent(menu_parent)

  normalized_route_path = normalize_route_path(route_path)
  validate_route_matches_menu_parent(normalized_route_path, menu_parent)

  page_title = f'{tag}管理'
  page_description = description or f'管理{tag}数据，支持查询、分页与新增、编辑、删除操作。'

  return FrontendScaffoldContext(
    module_name=module_name,
    module_pascal=entity_name,
    module_camel=file_stem,
    module_kebab=snake_to_kebab(module_name),
    tag=tag,
    page_title=page_title,
    page_description=page_description,
    api_base_path=normalize_api_base_path(api_base_path),
    api_dir=normalize_relative_dir(api_dir),
    type_dir=normalize_relative_dir(type_dir),
    view_dir=normalize_relative_dir(view_dir),
    store_dir=normalize_relative_dir(store_dir),
    view_name=view_name,
    with_store=with_store,
    menu_parent=menu_parent,
    route_path=normalized_route_path,
    route_name=normalize_required_text(route_name, 'route_name'),
    menu_id=normalize_required_text(menu_id, 'menu_id'),
    menu_title=normalize_required_text(menu_title or page_title, 'menu_title'),
    menu_icon=normalize_required_text(menu_icon, 'menu_icon'),
    function_code=normalize_optional_text(function_code),
    register_route=register_route,
    register_menu=register_menu,
    backend_menu_id=normalize_required_text(backend_menu_id, 'backend_menu_id'),
    register_backend_menu=register_backend_menu,
  )


def build_replacements(context: FrontendScaffoldContext) -> list[tuple[str, str]]:
  return [
    ('__MODULE_NAME__', context.module_name),
    ('__MODULE_PASCAL__', context.module_pascal),
    ('__MODULE_CAMEL__', context.module_camel),
    ('__MODULE_TAG__', context.tag),
    ('__PAGE_TITLE__', context.page_title),
    ('__PAGE_DESCRIPTION__', context.page_description),
    ('__API_BASE_PATH__', context.api_base_path),
    ('__API_DIR__', context.api_dir),
    ('__TYPE_DIR__', context.type_dir),
    ('__STORE_DIR__', context.store_dir),
  ]


def transform_content(content: str, replacements: list[tuple[str, str]]) -> str:
  transformed = content
  for source, target in replacements:
    transformed = transformed.replace(source, target)
  return transformed


def join_relative_path(base: str, *parts: str) -> Path:
  path = Path(*parts)
  if not base:
    return path
  return Path(base) / path


def build_target_files(src_root: Path, context: FrontendScaffoldContext) -> dict[str, Path]:
  targets = {
    'types.ts.tpl': src_root
    / join_relative_path('types', context.type_dir, f'{context.module_camel}.ts'),
    'api.ts.tpl': src_root / join_relative_path('api', context.api_dir, f'{context.module_camel}.ts'),
    'view.api.vue.tpl': src_root
    / join_relative_path('views', context.view_dir, f'{context.view_name}.vue'),
  }

  if context.with_store:
    targets['store.ts.tpl'] = src_root / join_relative_path(
      'stores',
      context.store_dir,
      f'{context.module_camel}.ts',
    )
    targets['view.store.vue.tpl'] = targets.pop('view.api.vue.tpl')

  return targets


def ensure_registry_file(path: Path, template: str) -> None:
  if path.exists():
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(template, encoding='utf-8')


def validate_registry_marker(text: str, marker: str, label: str) -> None:
  if marker not in text:
    raise ValueError(f'{label} 缺少脚手架插入标记: {marker}')


def render_route_entry(context: FrontendScaffoldContext) -> str:
  meta_parts = [
    'requiresAuth: true',
    f"title: '{escape_ts_string(context.page_title)}'",
  ]
  if context.function_code:
    meta_parts.append(f"functionCode: '{escape_ts_string(context.function_code)}'")

  return (
    '  {\n'
    f"    path: '{escape_ts_string(context.route_path)}',\n"
    f"    name: '{escape_ts_string(context.route_name)}',\n"
    f"    component: () => import('{escape_ts_string(build_view_import_path(context.view_dir, context.view_name))}'),\n"
    f"    meta: {{ {', '.join(meta_parts)} }},\n"
    '  },\n'
  )


def render_menu_entry(context: FrontendScaffoldContext) -> str:
  lines = [
    '    {',
    f"      id: '{escape_ts_string(context.menu_id)}',",
    f"      title: '{escape_ts_string(context.menu_title)}',",
    f"      path: '{escape_ts_string(context.route_path)}',",
    f"      icon: '{escape_ts_string(context.menu_icon)}',",
  ]
  if context.function_code:
    lines.append(f"      functionCode: '{escape_ts_string(context.function_code)}',")
  lines.append('    },')
  return '\n'.join(lines) + '\n'


def render_backend_menu_entry(context: FrontendScaffoldContext) -> str:
  lines = [
    '    {',
    f"      'id': '{escape_ts_string(context.backend_menu_id)}',",
    f"      'parentId': '{escape_ts_string('0' if context.menu_parent == 'root' else '')}',",
    f"      'name': '{escape_ts_string(context.menu_title)}',",
    f"      'label': '{escape_ts_string(context.menu_title)}',",
    f"      'path': '{escape_ts_string(context.route_path)}',",
    f"      'icon': '{escape_ts_string(context.menu_icon)}',",
    f"      'permission': '{escape_ts_string(context.function_code or '')}',",
    "      'type': '0',",
    "      'children': [],",
    '    },',
  ]
  return '\n'.join(lines) + '\n'


def validate_registration_conflicts(
  src_root: Path,
  backend_root: Path,
  context: FrontendScaffoldContext,
) -> None:
  if context.register_route:
    route_registry_path = src_root / ROUTE_REGISTRY_RELATIVE_PATH
    if route_registry_path.exists():
      route_registry_text = route_registry_path.read_text(encoding='utf-8')
      validate_registry_marker(route_registry_text, ROUTE_REGISTRY_MARKER, str(route_registry_path))
      if f"path: '{escape_ts_string(context.route_path)}'" in route_registry_text:
        raise FileExistsError(f'路由路径已存在: {context.route_path}')
      if f"name: '{escape_ts_string(context.route_name)}'" in route_registry_text:
        raise FileExistsError(f'路由名称已存在: {context.route_name}')

  if context.register_menu:
    menu_registry_path = src_root / MENU_REGISTRY_RELATIVE_PATH
    if menu_registry_path.exists():
      menu_registry_text = menu_registry_path.read_text(encoding='utf-8')
      marker = MENU_REGISTRY_MARKERS[context.menu_parent]
      validate_registry_marker(menu_registry_text, marker, str(menu_registry_path))
      if f"id: '{escape_ts_string(context.menu_id)}'" in menu_registry_text:
        raise FileExistsError(f'菜单 ID 已存在: {context.menu_id}')
      if f"path: '{escape_ts_string(context.route_path)}'" in menu_registry_text:
        raise FileExistsError(f'菜单路径已存在: {context.route_path}')

  if context.register_backend_menu:
    backend_menu_registry_path = backend_root / BACKEND_MENU_REGISTRY_RELATIVE_PATH
    if backend_menu_registry_path.exists():
      backend_menu_registry_text = backend_menu_registry_path.read_text(encoding='utf-8')
      marker = BACKEND_MENU_REGISTRY_MARKERS[context.menu_parent]
      validate_registry_marker(
        backend_menu_registry_text,
        marker,
        str(backend_menu_registry_path),
      )
      if f"'id': '{escape_ts_string(context.backend_menu_id)}'" in backend_menu_registry_text:
        raise FileExistsError(f'后端菜单 ID 已存在: {context.backend_menu_id}')
      if f"'path': '{escape_ts_string(context.route_path)}'" in backend_menu_registry_text:
        raise FileExistsError(f'后端菜单路径已存在: {context.route_path}')


def register_scaffold_integrations(
  src_root: Path,
  backend_root: Path,
  context: FrontendScaffoldContext,
) -> list[Path]:
  touched_files: list[Path] = []

  if context.register_route:
    route_registry_path = src_root / ROUTE_REGISTRY_RELATIVE_PATH
    ensure_registry_file(route_registry_path, ROUTE_REGISTRY_TEMPLATE)
    route_registry_text = route_registry_path.read_text(encoding='utf-8')
    validate_registry_marker(route_registry_text, ROUTE_REGISTRY_MARKER, str(route_registry_path))
    updated_route_registry_text = route_registry_text.replace(
      ROUTE_REGISTRY_MARKER,
      f'{render_route_entry(context)}{ROUTE_REGISTRY_MARKER}',
      1,
    )
    route_registry_path.write_text(updated_route_registry_text, encoding='utf-8')
    touched_files.append(route_registry_path)

  if context.register_menu:
    menu_registry_path = src_root / MENU_REGISTRY_RELATIVE_PATH
    ensure_registry_file(menu_registry_path, MENU_REGISTRY_TEMPLATE)
    menu_registry_text = menu_registry_path.read_text(encoding='utf-8')
    marker = MENU_REGISTRY_MARKERS[context.menu_parent]
    validate_registry_marker(menu_registry_text, marker, str(menu_registry_path))
    updated_menu_registry_text = menu_registry_text.replace(
      marker,
      f'{render_menu_entry(context)}{marker}',
      1,
    )
    menu_registry_path.write_text(updated_menu_registry_text, encoding='utf-8')
    touched_files.append(menu_registry_path)

  if context.register_backend_menu:
    backend_menu_registry_path = backend_root / BACKEND_MENU_REGISTRY_RELATIVE_PATH
    ensure_registry_file(backend_menu_registry_path, BACKEND_MENU_REGISTRY_TEMPLATE)
    backend_menu_registry_text = backend_menu_registry_path.read_text(encoding='utf-8')
    marker = BACKEND_MENU_REGISTRY_MARKERS[context.menu_parent]
    validate_registry_marker(
      backend_menu_registry_text,
      marker,
      str(backend_menu_registry_path),
    )
    updated_backend_menu_registry_text = backend_menu_registry_text.replace(
      marker,
      f'{render_backend_menu_entry(context)}{marker}',
      1,
    )
    backend_menu_registry_path.write_text(updated_backend_menu_registry_text, encoding='utf-8')
    touched_files.append(backend_menu_registry_path)

  return touched_files


def scaffold_frontend_module(
  *,
  context: FrontendScaffoldContext,
  template_root: Path,
  src_root: Path,
  backend_root: Path,
) -> list[Path]:
  if not template_root.exists():
    raise FileNotFoundError(f'模板目录不存在: {template_root}')

  target_files = build_target_files(src_root, context)
  for template_name in target_files:
    if not (template_root / template_name).exists():
      raise FileNotFoundError(f'模板文件不存在: {template_root / template_name}')

  conflicts = [path for path in target_files.values() if path.exists()]
  if conflicts:
    raise FileExistsError(f'目标文件已存在: {conflicts[0]}')

  validate_registration_conflicts(src_root, backend_root, context)

  replacements = build_replacements(context)
  created_files: list[Path] = []

  for template_name, target_path in target_files.items():
    target_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text = (template_root / template_name).read_text(encoding='utf-8')
    transformed_text = transform_content(raw_text, replacements)
    target_path.write_text(transformed_text, encoding='utf-8')
    created_files.append(target_path)

  created_files.extend(register_scaffold_integrations(src_root, backend_root, context))
  return created_files


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description='基于标准模板生成前端 CRUD 模块骨架')
  parser.add_argument('module_name', help='模块名，使用 snake_case，例如 quality_report')
  parser.add_argument('--tag', help='页面与业务标签，例如 质检报告')
  parser.add_argument('--api-base-path', help='接口基础路径，例如 /manage/api/qualityReport')
  parser.add_argument('--api-dir', default='system', help='src/api 下的目标子目录')
  parser.add_argument('--type-dir', default='system', help='src/types 下的目标子目录')
  parser.add_argument('--view-dir', default='system-admin', help='src/views 下的目标子目录')
  parser.add_argument('--store-dir', default='system', help='src/stores 下的目标子目录')
  parser.add_argument('--file-stem', help='生成文件名，默认使用 camelCase，例如 qualityReport')
  parser.add_argument('--entity-name', help='实体名，默认使用 PascalCase，例如 QualityReport')
  parser.add_argument('--view-name', help='页面组件文件名，默认 <EntityName>Management')
  parser.add_argument('--description', help='页面说明文案')
  parser.add_argument('--with-store', action='store_true', help='同时生成 Pinia store，并让页面接入 store')
  parser.add_argument(
    '--menu-parent',
    default='system',
    help='菜单挂载分组：root/system/sales/production，默认 system',
  )
  parser.add_argument('--route-path', help='前端路由路径，例如 /system/quality-report')
  parser.add_argument('--route-name', help='前端路由 name，例如 system-quality-report')
  parser.add_argument('--function-code', help='路由与菜单权限码，留空则不写入 functionCode')
  parser.add_argument('--menu-id', help='前端菜单 ID，默认与 route-name 一致')
  parser.add_argument('--backend-menu-id', help='后端菜单 ID，默认与 route-name 一致')
  parser.add_argument('--menu-title', help='前端菜单标题，默认使用页面标题')
  parser.add_argument('--menu-icon', default=DEFAULT_MENU_ICON, help='前端菜单图标，默认 Document')
  parser.add_argument(
    '--skip-route-registration',
    action='store_true',
    help='仅生成模块文件，不写入 scaffoldedRoutes.ts',
  )
  parser.add_argument(
    '--skip-menu-registration',
    action='store_true',
    help='仅生成模块文件，不写入 scaffoldMenuRegistry.ts',
  )
  parser.add_argument(
    '--skip-backend-menu-registration',
    action='store_true',
    help='仅生成前端模块文件，不写入后端 scaffold_menu_registry.py',
  )
  parser.add_argument('--template-root', default=str(DEFAULT_TEMPLATE_ROOT), help='模板目录路径')
  parser.add_argument('--src-root', default=str(DEFAULT_SRC_ROOT), help='src 根目录路径')
  parser.add_argument('--backend-root', default=str(DEFAULT_BACKEND_ROOT), help='backend 根目录路径')
  return parser


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)

  module_name = str(args.module_name).strip()
  menu_parent = normalize_required_text(str(args.menu_parent), 'menu_parent')
  default_entity_name = snake_to_pascal(module_name)
  file_stem = str(args.file_stem or snake_to_camel(module_name)).strip()
  entity_name = str(args.entity_name or default_entity_name).strip()
  view_name = str(args.view_name or f'{entity_name}Management').strip()
  tag = str(args.tag or entity_name).strip()
  api_base_path = str(args.api_base_path or default_api_base_path(module_name)).strip()
  route_path = str(args.route_path or default_route_path(module_name, menu_parent)).strip()
  route_name = str(args.route_name or default_route_name(module_name, menu_parent)).strip()
  menu_id = str(args.menu_id or default_menu_id(route_name)).strip()
  backend_menu_id = str(args.backend_menu_id or default_backend_menu_id(route_name)).strip()

  try:
    context = build_context(
      module_name=module_name,
      tag=tag,
      api_base_path=api_base_path,
      api_dir=str(args.api_dir),
      type_dir=str(args.type_dir),
      view_dir=str(args.view_dir),
      store_dir=str(args.store_dir),
      file_stem=file_stem,
      entity_name=entity_name,
      view_name=view_name,
      description=args.description,
      with_store=bool(args.with_store),
      menu_parent=menu_parent,
      route_path=route_path,
      route_name=route_name,
      menu_id=menu_id,
      menu_title=args.menu_title,
      menu_icon=str(args.menu_icon),
      function_code=args.function_code,
      register_route=not bool(args.skip_route_registration),
      register_menu=not bool(args.skip_menu_registration),
      backend_menu_id=backend_menu_id,
      register_backend_menu=not bool(args.skip_backend_menu_registration),
    )
    created_files = scaffold_frontend_module(
      context=context,
      template_root=Path(str(args.template_root)).expanduser().resolve(),
      src_root=Path(str(args.src_root)).expanduser().resolve(),
      backend_root=Path(str(args.backend_root)).expanduser().resolve(),
    )
  except (FileExistsError, FileNotFoundError, ValueError) as error:
    print(str(error), file=sys.stderr)
    return 1

  print(f'已生成前端模块: {context.module_name}')
  for created_file in created_files:
    print(created_file)
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
