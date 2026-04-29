from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def ok_response(data: Any = None, msg: str = 'success') -> dict[str, Any]:
  """Unified success response body."""

  return {'code': 0, 'msg': msg, 'data': data}


def fail_response(msg: str, code: int = 500, status_code: int = 200) -> JSONResponse:
  """Unified failure response body."""

  return JSONResponse(status_code=status_code, content={'code': code, 'msg': msg, 'data': None})

