from __future__ import annotations

from typing import Any


def insert_attachment(
  cur: Any,
  *,
  attachment_id: str,
  biz_type: str,
  biz_id: str,
  file_name: str,
  file_size: int,
  file_path: str,
  upload_by: str,
  upload_time: str,
) -> None:
  cur.execute(
    '''
    INSERT INTO attachments(id, biz_type, biz_id, file_name, file_size, file_path, upload_by, upload_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (attachment_id, biz_type, biz_id, file_name, file_size, file_path, upload_by, upload_time),
  )


def query_attachment_rows(cur: Any, biz_type: str, biz_id: str) -> list[Any]:
  cur.execute(
    '''
    SELECT id, biz_type, biz_id, file_name, file_size, file_path, upload_by, upload_time
    FROM attachments
    WHERE biz_type = ? AND biz_id = ?
    ORDER BY upload_time DESC
    ''',
    (biz_type, biz_id),
  )
  return cur.fetchall()


def fetch_attachment_file_path_row(cur: Any, attachment_id: str) -> Any:
  cur.execute('SELECT file_path FROM attachments WHERE id = ?', (attachment_id,))
  return cur.fetchone()


def delete_attachment(cur: Any, attachment_id: str) -> None:
  cur.execute('DELETE FROM attachments WHERE id = ?', (attachment_id,))


def fetch_attachment_download_row(cur: Any, attachment_id: str) -> Any:
  cur.execute('SELECT file_name, file_path FROM attachments WHERE id = ?', (attachment_id,))
  return cur.fetchone()
