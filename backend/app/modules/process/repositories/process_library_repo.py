from __future__ import annotations

from app.modules.process.deps import ProcessLibraryRouterDeps


def list_process_library_records(deps: ProcessLibraryRouterDeps) -> list[dict[str, object]]:
  return deps.get_process_library_records_func()
