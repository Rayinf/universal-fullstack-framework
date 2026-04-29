from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ProcessLibraryRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  get_process_library_records_func: Callable[[], list[dict[str, Any]]]
