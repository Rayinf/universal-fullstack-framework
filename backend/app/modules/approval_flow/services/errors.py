from __future__ import annotations


class ApprovalFlowServiceError(Exception):
  def __init__(self, message: str, code: int) -> None:
    super().__init__(message)
    self.message = message
    self.code = code
