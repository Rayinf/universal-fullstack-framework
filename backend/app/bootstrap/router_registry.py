from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.excel import export_to_excel
from app.core.runtime_helpers import load_name_maps
from app.modules.approval_flow.router import create_approval_flow_router
from app.modules.attachments.router import create_attachment_router
from app.modules.basic_info.router import create_basic_info_router
from app.modules.code_rule.router import create_code_rule_router
from app.modules.contracts.router import create_contract_router
from app.modules.customer.router import create_customer_router
from app.modules.device.router import create_device_router
from app.modules.inventory.router import create_inventory_router
from app.modules.local_crud.router import create_local_crud_router
from app.modules.notifications.router import create_notification_router
from app.modules.process.router import create_process_library_router, get_process_library_records
from app.modules.product_catalog.router import create_product_catalog_router
from app.modules.project.router import create_project_router
from app.modules.purchase_order.router import create_purchase_order_router
from app.modules.quotation.router import create_quotation_router
from app.modules.scan_binding.router import create_scan_binding_router
from app.modules.sys_backup.router import create_sys_backup_router
from app.modules.sys_log.router import create_sys_log_router
from app.modules.system.auth_router import create_auth_router
from app.modules.system.config_router import create_system_config_router
from app.modules.system.router import create_system_router
from app.modules.system_admin.dept_helpers import build_dept_tree, collect_descendant_ids
from app.modules.system_admin.dept_router import create_dept_read_router
from app.modules.system_admin.dept_write_router import create_dept_write_router
from app.modules.system_admin.role_router import create_role_router
from app.modules.system_admin.router import create_system_admin_router
from app.modules.system_admin.user_router import create_user_router
from app.modules.work_order.router import create_work_order_router
from app.modules.workstation.router import create_workstation_router
from app.bootstrap.scaffold_router_registry import scaffolded_router_registry


def register_scaffolded_routers(
  app: FastAPI,
  *,
  ok_func: Callable[..., dict[str, Any]],
  fail_func: Callable[..., JSONResponse],
  get_conn_func: Callable[[], Any],
) -> None:
  for entry in scaffolded_router_registry:
    module_path = str(entry.get('module', '')).strip()
    factory_name = str(entry.get('factory', '')).strip()
    if not module_path or not factory_name:
      continue

    module = import_module(module_path)
    factory = getattr(module, factory_name, None)
    if factory is None:
      raise AttributeError(f'未找到脚手架路由工厂: {module_path}.{factory_name}')

    app.include_router(
      factory(
        ok_func=ok_func,
        fail_func=fail_func,
        get_conn_func=get_conn_func,
      ),
    )


def register_routers(
  app: FastAPI,
  *,
  db_driver: str,
  uploads_dir: Path,
  menu_tree_func: Callable[[], list[dict[str, Any]]],
  ok_func: Callable[..., dict[str, Any]],
  fail_func: Callable[..., JSONResponse],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[..., int],
  safe_float_func: Callable[..., float],
  get_current_user_func: Callable[..., Any],
  verify_password_func: Callable[..., bool],
  build_token_func: Callable[..., str],
  parse_token_func: Callable[..., dict[str, Any] | None],
  access_token_expire_seconds: int,
  refresh_token_expire_seconds: int,
  hash_password_func: Callable[[str], str],
  create_notification_for_users_func: Callable[..., None],
) -> None:
  app.include_router(create_system_admin_router(ok_func=ok_func, get_conn_func=get_conn_func, menu_tree_func=menu_tree_func))
  app.include_router(create_system_router(ok_func=ok_func, db_driver=db_driver))
  app.include_router(
    create_auth_router(
      fail_func=fail_func,
      ok_func=ok_func,
      get_conn_func=get_conn_func,
      verify_password_func=verify_password_func,
      build_token_func=build_token_func,
      parse_token_func=parse_token_func,
      access_token_expire_seconds=access_token_expire_seconds,
      refresh_token_expire_seconds=refresh_token_expire_seconds,
    ),
  )
  app.include_router(
    create_system_config_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
    ),
  )
  app.include_router(
    create_customer_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
    ),
  )
  app.include_router(
    create_basic_info_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
    ),
  )
  app.include_router(
    create_process_library_router(
      ok_func=ok_func,
    ),
  )
  app.include_router(
    create_scan_binding_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
    ),
  )
  app.include_router(
    create_code_rule_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
    ),
  )
  app.include_router(
    create_sys_backup_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
    ),
  )
  app.include_router(
    create_approval_flow_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      get_process_library_records_func=get_process_library_records,
    ),
  )
  app.include_router(
    create_sys_log_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
    ),
  )
  app.include_router(
    create_device_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      load_name_maps_func=load_name_maps,
    ),
  )
  app.include_router(
    create_workstation_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      load_name_maps_func=load_name_maps,
    ),
  )
  app.include_router(
    create_dept_read_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      build_dept_tree_func=lambda include_users=True: build_dept_tree(get_conn_func, include_users=include_users),
    ),
  )
  app.include_router(
    create_dept_write_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      safe_int_func=safe_int_func,
      now_str_func=now_str_func,
      collect_descendant_ids_func=collect_descendant_ids,
    ),
  )
  app.include_router(
    create_role_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
    ),
  )
  app.include_router(
    create_user_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      hash_password_func=hash_password_func,
      get_current_user_func=get_current_user_func,
    ),
  )
  app.include_router(
    create_local_crud_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
    ),
  )
  app.include_router(
    create_project_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
    ),
  )
  app.include_router(
    create_purchase_order_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      safe_float_func=safe_float_func,
      get_current_user_func=get_current_user_func,
    ),
  )
  app.include_router(
    create_contract_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      safe_float_func=safe_float_func,
      get_current_user_func=get_current_user_func,
      export_to_excel_func=export_to_excel,
      create_notification_for_users_func=create_notification_for_users_func,
    ),
  )
  app.include_router(
    create_inventory_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      safe_float_func=safe_float_func,
    ),
  )
  app.include_router(
    create_product_catalog_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      safe_float_func=safe_float_func,
    ),
  )
  app.include_router(
    create_quotation_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      safe_float_func=safe_float_func,
      get_current_user_func=get_current_user_func,
      create_notification_for_users_func=create_notification_for_users_func,
    ),
  )
  app.include_router(
    create_work_order_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      now_str_func=now_str_func,
      safe_int_func=safe_int_func,
      safe_float_func=safe_float_func,
      get_current_user_func=get_current_user_func,
      export_to_excel_func=export_to_excel,
      create_notification_for_users_func=create_notification_for_users_func,
    ),
  )
  app.include_router(
    create_notification_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      get_current_user_func=get_current_user_func,
      safe_int_func=safe_int_func,
    ),
  )
  app.include_router(
    create_attachment_router(
      ok_func=ok_func,
      fail_func=fail_func,
      get_conn_func=get_conn_func,
      get_current_user_func=get_current_user_func,
      now_str_func=now_str_func,
      uploads_dir=uploads_dir,
    ),
  )
  register_scaffolded_routers(
    app,
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
  )
