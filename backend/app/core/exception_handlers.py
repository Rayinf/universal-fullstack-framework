from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _normalize_http_detail(detail: Any) -> str:
  if isinstance(detail, str):
    return detail
  if isinstance(detail, dict):
    text = str(detail.get('message') or detail.get('msg') or '').strip()
    if text:
      return text
  return '请求处理失败'


def register_exception_handlers(app: FastAPI) -> None:
  @app.exception_handler(RequestValidationError)
  async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    msg = str(first_error.get('msg') or '请求参数校验失败')
    return JSONResponse(status_code=422, content={'code': 422, 'msg': msg, 'data': None})

  @app.exception_handler(HTTPException)
  async def handle_http_error(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
      status_code=exc.status_code,
      content={'code': int(exc.status_code), 'msg': _normalize_http_detail(exc.detail), 'data': None},
    )

  @app.exception_handler(Exception)
  async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={'code': 500, 'msg': '服务器内部错误', 'data': None})

