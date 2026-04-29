from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote
import uuid


def resolve_upload_by(user: Any) -> str:
  return str(user['real_name']) if user else '系统'


def parse_attachment_filters(query_params: Any) -> tuple[str, str]:
  params = dict(query_params)
  return params.get('bizType', '').strip(), params.get('bizId', '').strip()


def build_attachment_save_info(uploads_dir: Path, file_name: str) -> dict[str, Any]:
  attachment_id = str(uuid.uuid4())
  date_dir = datetime.now().strftime('%Y%m%d')
  save_dir = uploads_dir / date_dir
  ext = Path(file_name).suffix
  save_name = f'{attachment_id}{ext}'
  return {
    'attachment_id': attachment_id,
    'save_dir': save_dir,
    'save_path': save_dir / save_name,
    'relative_path': f'{date_dir}/{save_name}',
  }


def iter_attachment_file(file_path: Path) -> Any:
  with open(file_path, 'rb') as file_obj:
    while chunk := file_obj.read(8192):
      yield chunk


def encode_attachment_filename(file_name: str) -> str:
  return quote(file_name)
