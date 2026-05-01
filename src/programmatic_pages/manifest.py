"""Build manifest writer."""

import json
import os
from datetime import datetime, timezone
from typing import Any


def write_manifest(
    output_dir: str,
    *,
    project_key: str,
    base_url: str,
    pages_built: int,
    pages_errors: int,
    build_time_seconds: float,
    entity_type_filter: str | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    """Write manifest.json into the build output directory. Returns its path."""
    manifest = {
        "project_key": project_key,
        "base_url": base_url,
        "output_dir": output_dir,
        "pages_built": pages_built,
        "pages_errors": pages_errors,
        "build_time_seconds": round(build_time_seconds, 1),
        "built_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "entity_type_filter": entity_type_filter,
    }
    if extra:
        manifest.update(extra)

    path = os.path.join(output_dir, "manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return path
