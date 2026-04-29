from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ExampleRouterDeps:
  ok_func: Callable[[Any, str], dict[str, Any]]
  fail_func: Callable[[str, int], Any]
  get_conn_func: Callable[[], Any]
