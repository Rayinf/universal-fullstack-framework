from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.modules.system_admin.deps import DeptReadRouterDeps
from app.modules.system_admin.helpers import query_value, to_int
from app.modules.system_admin.services.dept_query_service import (
  get_dept_by_id_detail,
  get_dept_by_name_detail,
  get_dept_tree,
  query_dept_page,
)
from app.modules.system_admin.services.errors import SystemAdminServiceError


def register_dept_read_routes(router: APIRouter, deps: DeptReadRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.get('/admin/dept/tree')
  def dept_tree() -> dict[str, Any]:
    return ok_func(get_dept_tree(deps, include_users=True), 'success')

  @router.get('/admin/dept/user-tree')
  def user_dept_tree() -> dict[str, Any]:
    return ok_func(get_dept_tree(deps, include_users=True), 'success')

  @router.get('/admin/dept/page')
  def page_depts(request: Request) -> dict[str, Any]:
    query = request.query_params
    return ok_func(
      query_dept_page(
        deps,
        current=to_int(query_value(query, ['current', 'page.current', 'page[current]'], '1'), 1),
        size=to_int(query_value(query, ['size', 'page.size', 'page[size]'], '10'), 10),
        name=query_value(query, ['name', 'dto.name', 'dto[name]']),
        parent_id=query_value(query, ['parentId', 'dto.parentId', 'dto[parentId]']),
      ),
      'success',
    )

  @router.get('/admin/dept/details/{dept_name}')
  def dept_detail_by_name(dept_name: str) -> Any:
    try:
      return ok_func(get_dept_by_name_detail(deps, dept_name=dept_name), 'success')
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)

  @router.get('/admin/dept/{dept_id}')
  def dept_detail_by_id(dept_id: str) -> Any:
    try:
      return ok_func(get_dept_by_id_detail(deps, dept_id=dept_id), 'success')
    except SystemAdminServiceError as error:
      return fail_func(error.message, error.code)
