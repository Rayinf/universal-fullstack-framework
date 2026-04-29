from __future__ import annotations

from typing import Any

from fastapi import Request, UploadFile

from app.modules.attachments.deps import AttachmentRouterDeps
from app.modules.attachments.helpers import build_attachment_save_info, resolve_upload_by
from app.modules.attachments.repositories.attachment_repo import (
  delete_attachment as delete_attachment_row,
  fetch_attachment_file_path_row,
  insert_attachment,
)
from app.modules.attachments.serializers import build_attachment_upload_result
from app.modules.attachments.services.errors import AttachmentServiceError


async def create_attachment(
  deps: AttachmentRouterDeps,
  request: Request,
  *,
  file: UploadFile,
  biz_type: str,
  biz_id: str,
) -> dict[str, Any]:
  user = deps.get_current_user_func(request)
  upload_by = resolve_upload_by(user)
  if not file.filename:
    raise AttachmentServiceError('文件名不能为空', 400)

  save_info = build_attachment_save_info(deps.uploads_dir, file.filename)
  save_info['save_dir'].mkdir(parents=True, exist_ok=True)

  content = await file.read()
  file_size = len(content)
  save_info['save_path'].write_bytes(content)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  insert_attachment(
    cur,
    attachment_id=save_info['attachment_id'],
    biz_type=biz_type,
    biz_id=biz_id,
    file_name=file.filename,
    file_size=file_size,
    file_path=save_info['relative_path'],
    upload_by=upload_by,
    upload_time=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return build_attachment_upload_result(
    save_info['attachment_id'],
    file.filename,
    file_size,
    deps.now_str_func(),
  )


def delete_attachment(deps: AttachmentRouterDeps, *, attachment_id: str) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_attachment_file_path_row(cur, attachment_id)
  if not row:
    conn.close()
    raise AttachmentServiceError('附件不存在', 400)

  file_path = deps.uploads_dir / str(row['file_path'])
  if file_path.exists():
    file_path.unlink()

  delete_attachment_row(cur, attachment_id)
  conn.commit()
  conn.close()
  return True
