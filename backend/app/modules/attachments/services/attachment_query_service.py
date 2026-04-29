from __future__ import annotations

from pathlib import Path
from typing import Any

from app.modules.attachments.deps import AttachmentRouterDeps
from app.modules.attachments.helpers import parse_attachment_filters
from app.modules.attachments.repositories.attachment_repo import (
  fetch_attachment_download_row,
  query_attachment_rows,
)
from app.modules.attachments.serializers import attachment_to_dict
from app.modules.attachments.services.errors import AttachmentServiceError


def query_attachment_list(deps: AttachmentRouterDeps, query_params: Any) -> list[dict[str, Any]]:
  biz_type, biz_id = parse_attachment_filters(query_params)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_attachment_rows(cur, biz_type, biz_id)
  conn.close()
  return [attachment_to_dict(row) for row in rows]


def get_attachment_download_payload(deps: AttachmentRouterDeps, *, attachment_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_attachment_download_row(cur, attachment_id)
  conn.close()
  if not row:
    raise AttachmentServiceError('附件不存在', 404)

  file_path = deps.uploads_dir / str(row['file_path'])
  if not file_path.exists():
    raise AttachmentServiceError('文件已丢失', 404)

  return {
    'file_name': str(row['file_name']),
    'file_path': Path(file_path),
  }
