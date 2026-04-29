from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_ROOT = BACKEND_ROOT / 'app' / 'modules' / '_template' / 'backend_module'
DEFAULT_OUTPUT_ROOT = BACKEND_ROOT / 'app' / 'modules'
DEFAULT_BOOTSTRAP_ROOT = BACKEND_ROOT / 'app' / 'bootstrap'
MODULE_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')
ROUTER_REGISTRY_RELATIVE_PATH = Path('scaffold_router_registry.py')
ROUTER_REGISTRY_MARKER = '  # __SCAFFOLD_ROUTER_ENTRIES__'
ROUTER_REGISTRY_TEMPLATE = """from __future__ import annotations

scaffolded_router_registry: list[dict[str, str]] = [
  # __SCAFFOLD_ROUTER_ENTRIES__
]
"""


def snake_to_pascal(name: str) -> str:
  return ''.join(part.capitalize() for part in name.split('_') if part)


def default_resource_path(module_name: str) -> str:
  return f"/{module_name.replace('_', '-')}"


def validate_module_name(module_name: str) -> None:
  if not MODULE_NAME_PATTERN.match(module_name):
    raise ValueError('module_name 必须是 snake_case，且只能包含小写字母、数字、下划线')


def normalize_resource_path(resource_path: str) -> str:
  normalized = resource_path.strip() or '/'
  if not normalized.startswith('/'):
    normalized = f'/{normalized}'
  if len(normalized) > 1 and normalized.endswith('/'):
    normalized = normalized.rstrip('/')
  return normalized


def rename_path_part(part: str, module_name: str) -> str:
  replacements = {
    'example_routes.py': f'{module_name}_routes.py',
    'example_query_service.py': f'{module_name}_query_service.py',
    'example_command_service.py': f'{module_name}_command_service.py',
    'example_repo.py': f'{module_name}_repo.py',
  }
  return replacements.get(part, part)


def build_replacements(
  *,
  module_name: str,
  tag: str,
  resource_path: str,
  table_name: str,
) -> list[tuple[str, str]]:
  class_prefix = snake_to_pascal(module_name)
  return [
    ('app.modules._template.backend_module', f'app.modules.{module_name}'),
    ('ExampleModuleServiceError', f'{class_prefix}ServiceError'),
    ('ExampleRouterDeps', f'{class_prefix}RouterDeps'),
    ('register_example_routes', f'register_{module_name}_routes'),
    ('create_example_router', f'create_{module_name}_router'),
    ('query_example_page_total', f'query_{module_name}_page_total'),
    ('query_example_page_rows', f'query_{module_name}_page_rows'),
    ('create_example_record', f'create_{module_name}_record'),
    ('insert_example_record', f'insert_{module_name}_record'),
    ('query_example_page', f'query_{module_name}_page'),
    ('page_example', f'page_{module_name}'),
    ('create_example', f'create_{module_name}'),
    ('example_query_service', f'{module_name}_query_service'),
    ('example_command_service', f'{module_name}_command_service'),
    ('example_routes', f'{module_name}_routes'),
    ('example_repo', f'{module_name}_repo'),
    ('/example/page', f'{resource_path}/page'),
    ('/example', resource_path),
    ('example_table', table_name),
    ('示例模板模块', tag),
    ('标准后端模块模板示例。', f'{tag} 模块。'),
  ]


def transform_content(content: str, replacements: list[tuple[str, str]]) -> str:
  transformed = content
  for source, target in replacements:
    transformed = transformed.replace(source, target)
  return transformed


def ensure_registry_file(path: Path, template: str) -> None:
  if path.exists():
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(template, encoding='utf-8')


def validate_registry_marker(text: str, marker: str, label: str) -> None:
  if marker not in text:
    raise ValueError(f'{label} 缺少脚手架插入标记: {marker}')


def render_router_registry_entry(module_name: str) -> str:
  return (
    '  {\n'
    f"    'module': 'app.modules.{module_name}.router',\n"
    f"    'factory': 'create_{module_name}_router',\n"
    '  },\n'
  )


def validate_router_registry_conflicts(bootstrap_root: Path, module_name: str) -> None:
  registry_path = bootstrap_root / ROUTER_REGISTRY_RELATIVE_PATH
  if not registry_path.exists():
    return

  registry_text = registry_path.read_text(encoding='utf-8')
  validate_registry_marker(registry_text, ROUTER_REGISTRY_MARKER, str(registry_path))
  module_path = f"'module': 'app.modules.{module_name}.router'"
  factory_name = f"'factory': 'create_{module_name}_router'"
  if module_path in registry_text or factory_name in registry_text:
    raise FileExistsError(f'路由注册已存在: {module_name}')


def register_scaffolded_router(bootstrap_root: Path, module_name: str) -> Path:
  registry_path = bootstrap_root / ROUTER_REGISTRY_RELATIVE_PATH
  ensure_registry_file(registry_path, ROUTER_REGISTRY_TEMPLATE)
  registry_text = registry_path.read_text(encoding='utf-8')
  validate_registry_marker(registry_text, ROUTER_REGISTRY_MARKER, str(registry_path))
  updated_registry_text = registry_text.replace(
    ROUTER_REGISTRY_MARKER,
    f'{render_router_registry_entry(module_name)}{ROUTER_REGISTRY_MARKER}',
    1,
  )
  registry_path.write_text(updated_registry_text, encoding='utf-8')
  return registry_path


def scaffold_backend_module(
  *,
  module_name: str,
  template_root: Path,
  output_root: Path,
  bootstrap_root: Path,
  resource_path: str,
  table_name: str,
  tag: str,
  register_router: bool,
) -> list[Path]:
  validate_module_name(module_name)
  if not template_root.exists():
    raise FileNotFoundError(f'模板目录不存在: {template_root}')

  target_root = output_root / module_name
  if target_root.exists():
    raise FileExistsError(f'目标模块目录已存在: {target_root}')
  if register_router:
    validate_router_registry_conflicts(bootstrap_root, module_name)

  replacements = build_replacements(
    module_name=module_name,
    tag=tag,
    resource_path=normalize_resource_path(resource_path),
    table_name=table_name,
  )

  created_files: list[Path] = []
  for source_path in sorted(template_root.rglob('*')):
    relative_path = source_path.relative_to(template_root)
    if any(part.startswith('._') for part in relative_path.parts):
      continue

    target_relative = Path(*(rename_path_part(part, module_name) for part in relative_path.parts))
    target_path = target_root / target_relative

    if source_path.is_dir():
      target_path.mkdir(parents=True, exist_ok=True)
      continue

    target_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text = source_path.read_text(encoding='utf-8')
    target_path.write_text(transform_content(raw_text, replacements), encoding='utf-8')
    created_files.append(target_path)

  if register_router:
    created_files.append(register_scaffolded_router(bootstrap_root, module_name))

  return created_files


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description='基于标准模板生成后端模块骨架')
  parser.add_argument('module_name', help='模块名，使用 snake_case，例如 quality_report')
  parser.add_argument('--resource-path', help='默认路由资源路径，例如 /manage/api/qualityReport')
  parser.add_argument('--table-name', help='默认 SQL 表名')
  parser.add_argument('--tag', help='FastAPI 标签名')
  parser.add_argument('--template-root', default=str(DEFAULT_TEMPLATE_ROOT), help='模板目录路径')
  parser.add_argument('--output-root', default=str(DEFAULT_OUTPUT_ROOT), help='模块输出根目录')
  parser.add_argument('--bootstrap-root', default=str(DEFAULT_BOOTSTRAP_ROOT), help='bootstrap 根目录')
  parser.add_argument(
    '--skip-router-registration',
    action='store_true',
    help='仅生成模块文件，不写入 scaffold_router_registry.py',
  )
  return parser


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)

  module_name = str(args.module_name).strip()
  resource_path = str(args.resource_path or default_resource_path(module_name)).strip()
  table_name = str(args.table_name or f'{module_name}_table').strip()
  tag = str(args.tag or module_name).strip()

  try:
    created_files = scaffold_backend_module(
      module_name=module_name,
      template_root=Path(str(args.template_root)).expanduser().resolve(),
      output_root=Path(str(args.output_root)).expanduser().resolve(),
      bootstrap_root=Path(str(args.bootstrap_root)).expanduser().resolve(),
      resource_path=resource_path,
      table_name=table_name,
      tag=tag,
      register_router=not bool(args.skip_router_registration),
    )
  except (FileExistsError, FileNotFoundError, ValueError) as error:
    print(str(error), file=sys.stderr)
    return 1

  print(f'已生成模块: {module_name}')
  for created_file in created_files:
    print(created_file)
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
