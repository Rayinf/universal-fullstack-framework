from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.modules.attachments.deps import AttachmentRouterDeps
from app.modules.attachments.helpers import encode_attachment_filename, iter_attachment_file
from app.modules.attachments.services.attachment_command_service import (
  create_attachment as create_attachment_command,
  delete_attachment as delete_attachment_command,
)
from app.modules.attachments.services.attachment_query_service import (
  get_attachment_download_payload,
  query_attachment_list,
)
from app.modules.attachments.services.errors import AttachmentServiceError


def register_attachment_routes(router: APIRouter, deps: AttachmentRouterDeps) -> None:
  ok_func = deps.ok_func
  fail_func = deps.fail_func

  @router.post('/local/attachments/upload')
  async def upload_attachment(
    request: Request,
    file: UploadFile = File(...),
    bizType: str = Form(''),
    bizId: str = Form(''),
  ) -> dict[str, Any] | Any:
    try:
      data = await create_attachment_command(
        deps,
        request,
        file=file,
        biz_type=bizType,
        biz_id=bizId,
      )
    except AttachmentServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(data, 'success')

  @router.get('/local/attachments/list')
  def list_attachments(request: Request) -> dict[str, Any]:
    return ok_func(query_attachment_list(deps, request.query_params), 'success')

  @router.delete('/local/attachments/{attachment_id}')
  def delete_attachment(attachment_id: str) -> dict[str, Any] | Any:
    try:
      delete_attachment_command(deps, attachment_id=attachment_id)
    except AttachmentServiceError as error:
      return fail_func(error.message, error.code)
    return ok_func(True, 'success')

  @router.get('/local/attachments/download/{attachment_id}')
  def download_attachment(attachment_id: str) -> Any:
    try:
      payload = get_attachment_download_payload(deps, attachment_id=attachment_id)
    except AttachmentServiceError as error:
      return JSONResponse(status_code=error.code, content={'code': error.code, 'msg': error.message})

    encoded_name = encode_attachment_filename(payload['file_name'])
    return StreamingResponse(
      iter_attachment_file(payload['file_path']),
      media_type='application/octet-stream',
      headers={'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_name}"},
    )
