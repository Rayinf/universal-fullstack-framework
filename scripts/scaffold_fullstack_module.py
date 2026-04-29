from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from backend.scripts import scaffold_backend_module as backend_scaffold
from scripts import scaffold_frontend_module as frontend_scaffold


@dataclass(frozen=True)
class FrontendDirDefaults:
  api_dir: str
  type_dir: str
  view_dir: str
  store_dir: str


@dataclass(frozen=True)
class FileSnapshot:
  path: Path
  existed: bool
  content: str | None


@dataclass(frozen=True)
class FullstackScaffoldConfig:
  module_name: str
  tag: str
  resource_path: str
  table_name: str
  frontend_context: frontend_scaffold.FrontendScaffoldContext
  frontend_template_root: Path
  backend_template_root: Path
  src_root: Path
  backend_root: Path
  backend_output_root: Path
  backend_bootstrap_root: Path


FRONTEND_DIR_DEFAULTS: dict[str, FrontendDirDefaults] = {
  'root': FrontendDirDefaults(
    api_dir='system',
    type_dir='system',
    view_dir='system',
    store_dir='system',
  ),
  'system': FrontendDirDefaults(
    api_dir='system',
    type_dir='system',
    view_dir='system-admin',
    store_dir='system',
  ),
  'sales': FrontendDirDefaults(
    api_dir='sales',
    type_dir='sales',
    view_dir='sales',
    store_dir='sales',
  ),
  'production': FrontendDirDefaults(
    api_dir='production',
    type_dir='production',
    view_dir='production',
    store_dir='production',
  ),
}


def resolve_frontend_dir(value: str | None, default_value: str) -> str:
  normalized = frontend_scaffold.normalize_optional_text(value)
  if normalized is None:
    return default_value
  return normalized


def capture_snapshot(path: Path) -> FileSnapshot:
  if path.exists():
    return FileSnapshot(path=path, existed=True, content=path.read_text(encoding='utf-8'))
  return FileSnapshot(path=path, existed=False, content=None)


def restore_snapshot(snapshot: FileSnapshot) -> None:
  if snapshot.existed:
    snapshot.path.parent.mkdir(parents=True, exist_ok=True)
    snapshot.path.write_text(snapshot.content or '', encoding='utf-8')
    return
  if snapshot.path.exists():
    snapshot.path.unlink()


def build_config(argv: list[str] | None = None) -> FullstackScaffoldConfig:
  parser = build_parser()
  args = parser.parse_args(argv)

  module_name = str(args.module_name).strip()
  menu_parent = frontend_scaffold.normalize_required_text(str(args.menu_parent), 'menu_parent')
  dir_defaults = FRONTEND_DIR_DEFAULTS.get(menu_parent)
  if dir_defaults is None:
    frontend_scaffold.validate_menu_parent(menu_parent)
    raise ValueError(f'不支持的 menu_parent: {menu_parent}')

  default_entity_name = frontend_scaffold.snake_to_pascal(module_name)
  entity_name = str(args.entity_name or default_entity_name).strip()
  file_stem = str(args.file_stem or frontend_scaffold.snake_to_camel(module_name)).strip()
  view_name = str(args.view_name or f'{entity_name}Management').strip()
  tag = str(args.tag or entity_name).strip()
  resource_path = str(args.api_base_path or frontend_scaffold.default_api_base_path(module_name)).strip()
  route_path = str(args.route_path or frontend_scaffold.default_route_path(module_name, menu_parent)).strip()
  route_name = str(args.route_name or frontend_scaffold.default_route_name(module_name, menu_parent)).strip()
  menu_id = route_name
  backend_menu_id = route_name

  frontend_context = frontend_scaffold.build_context(
    module_name=module_name,
    tag=tag,
    api_base_path=resource_path,
    api_dir=resolve_frontend_dir(args.api_dir, dir_defaults.api_dir),
    type_dir=resolve_frontend_dir(args.type_dir, dir_defaults.type_dir),
    view_dir=resolve_frontend_dir(args.view_dir, dir_defaults.view_dir),
    store_dir=resolve_frontend_dir(args.store_dir, dir_defaults.store_dir),
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
    register_route=True,
    register_menu=True,
    backend_menu_id=backend_menu_id,
    register_backend_menu=True,
  )

  return FullstackScaffoldConfig(
    module_name=module_name,
    tag=tag,
    resource_path=resource_path,
    table_name=str(args.table_name or f'{module_name}_table').strip(),
    frontend_context=frontend_context,
    frontend_template_root=Path(str(args.frontend_template_root)).expanduser().resolve(),
    backend_template_root=Path(str(args.backend_template_root)).expanduser().resolve(),
    src_root=Path(str(args.src_root)).expanduser().resolve(),
    backend_root=Path(str(args.backend_root)).expanduser().resolve(),
    backend_output_root=Path(str(args.backend_output_root)).expanduser().resolve(),
    backend_bootstrap_root=Path(str(args.backend_bootstrap_root)).expanduser().resolve(),
  )


def validate_frontend_preconditions(
  config: FullstackScaffoldConfig,
) -> dict[str, Path]:
  if not config.frontend_template_root.exists():
    raise FileNotFoundError(f'前端模板目录不存在: {config.frontend_template_root}')

  target_files = frontend_scaffold.build_target_files(config.src_root, config.frontend_context)
  for template_name in target_files:
    template_path = config.frontend_template_root / template_name
    if not template_path.exists():
      raise FileNotFoundError(f'前端模板文件不存在: {template_path}')

  conflicts = [path for path in target_files.values() if path.exists()]
  if conflicts:
    raise FileExistsError(f'目标文件已存在: {conflicts[0]}')

  frontend_scaffold.validate_registration_conflicts(
    config.src_root,
    config.backend_root,
    config.frontend_context,
  )
  return target_files


def validate_backend_preconditions(config: FullstackScaffoldConfig) -> Path:
  backend_scaffold.validate_module_name(config.module_name)
  if not config.backend_template_root.exists():
    raise FileNotFoundError(f'后端模板目录不存在: {config.backend_template_root}')

  module_root = config.backend_output_root / config.module_name
  if module_root.exists():
    raise FileExistsError(f'目标模块目录已存在: {module_root}')

  backend_scaffold.validate_router_registry_conflicts(
    config.backend_bootstrap_root,
    config.module_name,
  )
  return module_root


def collect_registry_snapshots(config: FullstackScaffoldConfig) -> list[FileSnapshot]:
  snapshots = [
    capture_snapshot(config.src_root / frontend_scaffold.ROUTE_REGISTRY_RELATIVE_PATH),
    capture_snapshot(config.src_root / frontend_scaffold.MENU_REGISTRY_RELATIVE_PATH),
    capture_snapshot(
      config.backend_root / frontend_scaffold.BACKEND_MENU_REGISTRY_RELATIVE_PATH,
    ),
    capture_snapshot(
      config.backend_bootstrap_root / backend_scaffold.ROUTER_REGISTRY_RELATIVE_PATH,
    ),
  ]
  return snapshots


def rollback_scaffold(
  *,
  module_root: Path,
  frontend_target_files: dict[str, Path],
  snapshots: list[FileSnapshot],
) -> None:
  for target_path in frontend_target_files.values():
    if target_path.exists():
      target_path.unlink()

  if module_root.exists():
    shutil.rmtree(module_root)

  for snapshot in snapshots:
    restore_snapshot(snapshot)


def scaffold_fullstack_module(config: FullstackScaffoldConfig) -> list[Path]:
  frontend_target_files = validate_frontend_preconditions(config)
  module_root = validate_backend_preconditions(config)
  snapshots = collect_registry_snapshots(config)

  try:
    created_backend_files = backend_scaffold.scaffold_backend_module(
      module_name=config.module_name,
      template_root=config.backend_template_root,
      output_root=config.backend_output_root,
      bootstrap_root=config.backend_bootstrap_root,
      resource_path=config.resource_path,
      table_name=config.table_name,
      tag=config.tag,
      register_router=True,
    )
    created_frontend_files = frontend_scaffold.scaffold_frontend_module(
      context=config.frontend_context,
      template_root=config.frontend_template_root,
      src_root=config.src_root,
      backend_root=config.backend_root,
    )
  except Exception:
    rollback_scaffold(
      module_root=module_root,
      frontend_target_files=frontend_target_files,
      snapshots=snapshots,
    )
    raise

  return [*created_backend_files, *created_frontend_files]


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description='一次生成前后端模块骨架并完成注册表接线')
  parser.add_argument('module_name', help='模块名，使用 snake_case，例如 quality_report')
  parser.add_argument('--tag', help='页面与后端路由标签，例如 质检报告')
  parser.add_argument(
    '--api-base-path',
    '--resource-path',
    dest='api_base_path',
    help='前后端共用接口基础路径，例如 /manage/api/qualityReport',
  )
  parser.add_argument('--table-name', help='后端仓储默认表名，例如 quality_report_records')
  parser.add_argument('--with-store', action='store_true', help='前端同时生成 Pinia store')
  parser.add_argument(
    '--menu-parent',
    default='system',
    help='菜单挂载分组：root/system/sales/production，默认 system',
  )
  parser.add_argument('--route-path', help='前端路由路径，例如 /system/quality-report')
  parser.add_argument('--route-name', help='前端路由 name，例如 system-quality-report')
  parser.add_argument('--function-code', help='前后端共用权限码')
  parser.add_argument('--menu-title', help='前后端菜单标题，默认使用 <tag>管理')
  parser.add_argument(
    '--menu-icon',
    default=frontend_scaffold.DEFAULT_MENU_ICON,
    help='前端菜单图标，默认 Document',
  )
  parser.add_argument('--description', help='前端页面说明文案')
  parser.add_argument('--file-stem', help='前端文件名 stem，默认 camelCase')
  parser.add_argument('--entity-name', help='前端实体 PascalCase 名称')
  parser.add_argument('--view-name', help='前端页面组件名，默认 <EntityName>Management')
  parser.add_argument('--api-dir', help='前端 api 子目录，默认跟随 menu_parent')
  parser.add_argument('--type-dir', help='前端 types 子目录，默认跟随 menu_parent')
  parser.add_argument('--view-dir', help='前端 views 子目录，默认跟随 menu_parent')
  parser.add_argument('--store-dir', help='前端 stores 子目录，默认跟随 menu_parent')
  parser.add_argument(
    '--frontend-template-root',
    default=str(frontend_scaffold.DEFAULT_TEMPLATE_ROOT),
    help='前端模板目录路径',
  )
  parser.add_argument(
    '--backend-template-root',
    default=str(backend_scaffold.DEFAULT_TEMPLATE_ROOT),
    help='后端模板目录路径',
  )
  parser.add_argument('--src-root', default=str(frontend_scaffold.DEFAULT_SRC_ROOT), help='src 根目录路径')
  parser.add_argument(
    '--backend-root',
    default=str(frontend_scaffold.DEFAULT_BACKEND_ROOT),
    help='backend 根目录路径，用于后端菜单注册',
  )
  parser.add_argument(
    '--backend-output-root',
    default=str(backend_scaffold.DEFAULT_OUTPUT_ROOT),
    help='后端模块输出根目录',
  )
  parser.add_argument(
    '--backend-bootstrap-root',
    default=str(backend_scaffold.DEFAULT_BOOTSTRAP_ROOT),
    help='后端 bootstrap 根目录',
  )
  return parser


def main(argv: list[str] | None = None) -> int:
  try:
    config = build_config(argv)
    created_files = scaffold_fullstack_module(config)
  except (FileExistsError, FileNotFoundError, ValueError) as error:
    print(str(error), file=sys.stderr)
    return 1
  except Exception as error:
    print(f'全栈脚手架执行失败，已回滚: {error}', file=sys.stderr)
    return 1

  print(f'已生成全栈模块: {config.module_name}')
  for created_file in created_files:
    print(created_file)
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
