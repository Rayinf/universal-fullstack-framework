from __future__ import annotations

from typing import Any


def attachment_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'bizType': row['biz_type'],
    'bizId': row['biz_id'],
    'fileName': row['file_name'],
    'fileSize': int(row['file_size']),
    'filePath': row['file_path'],
    'uploadBy': row['upload_by'] or '',
    'uploadTime': row['upload_time'] or '',
  }


def build_attachment_upload_result(
  attachment_id: str,
  file_name: str,
  file_size: int,
  upload_time: str,
) -> dict[str, Any]:
  return {
    'id': attachment_id,
    'fileName': file_name,
    'fileSize': file_size,
    'uploadTime': upload_time,
  }
