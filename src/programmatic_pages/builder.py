"""Render + write loop. Operates only on RenderablePage dataclasses."""

import os
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from django.template import Template

from programmatic_pages.adapter import ProjectConfig, RenderablePage
from programmatic_pages.schema import build_schema_json


def render_page(
    page: RenderablePage,
    project: ProjectConfig,
    template: Template,
    *,
    year: int | None = None,
) -> str:
    """Render one RenderablePage to an HTML string."""
    from django.template import Context

    schema_json = build_schema_json(page, project)
    canonical_url = _canonical_url(page, project)

    context = Context(
        {
            "title": page.title,
            # Escaped once, by template autoescaping. Pre-escaping here produced &amp;quot;.
            "meta_description": page.meta_description or "",
            "canonical_url": canonical_url,
            "h1": page.h1 or page.title,
            "body_html": page.body_html or "",
            "schema_json": schema_json,
            "base_url": project.base_url.rstrip("/"),
            "site_name": project.site_name,
            "ga_id": project.ga_measurement_id,
            "year": year or datetime.now().year,
            "breadcrumb_chain": page.breadcrumb_chain,
            **page.extra_context,
        }
    )
    return template.render(context)


def write_page(output_dir: str, url_path: str, html: str) -> str:
    """Write rendered HTML to filesystem at output_dir/url_path/index.html.

    Raises ValueError if url_path would land outside output_dir (for example "../x/").
    """
    clean = url_path.strip("/")
    root = os.path.realpath(output_dir)
    file_dir = os.path.realpath(os.path.join(root, clean)) if clean else root
    if os.path.commonpath([root, file_dir]) != root:
        raise ValueError(f"url_path {url_path!r} resolves outside the output directory")
    Path(file_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(file_dir, "index.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return file_path


@dataclass
class BuildResult:
    pages_built: int
    pages_errors: int
    elapsed_seconds: float
    # One "url_path: reason" line per failed page, so a failure can be read, not just counted.
    errors: list[str] = field(default_factory=list)


def build(
    pages: Iterable[RenderablePage],
    project: ProjectConfig,
    template: Template,
    output_dir: str,
    *,
    concurrency: int = 4,
    on_progress: Callable[[int, int, int, float], None] | None = None,
    log_interval: int = 1000,
) -> BuildResult:
    """Render+write all pages in parallel. Returns counts and elapsed time.

    `on_progress(done, built, errors, rate)` fires every `log_interval` pages.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # One file per url_path. A second page with the same path would silently overwrite the
    # first and still be counted as built, so it is reported as an error instead.
    pages_list: list[RenderablePage] = []
    error_lines: list[str] = []
    seen: set[str] = set()
    for page in pages:
        key = page.url_path.strip("/")
        if key in seen:
            error_lines.append(f"{page.url_path}: duplicate url_path, page skipped")
            continue
        seen.add(key)
        pages_list.append(page)

    total = len(pages_list) + len(error_lines)
    t_start = time.time()
    built = 0
    errors = len(error_lines)

    def _build_one(page: RenderablePage) -> tuple[str, str]:
        try:
            html = render_page(page, project, template)
            write_page(output_dir, page.url_path, html)
            return ("ok", page.url_path)
        except Exception as e:  # noqa: BLE001
            return ("error", f"{page.url_path}: {e}")

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(_build_one, p): p for p in pages_list}
        for future in as_completed(futures):
            kind, detail = future.result()
            if kind == "ok":
                built += 1
            else:
                errors += 1
                error_lines.append(detail)
            done = built + errors
            if on_progress and (done % log_interval == 0 or done == total):
                elapsed = time.time() - t_start
                rate = done / elapsed if elapsed > 0 else 0
                on_progress(done, built, errors, rate)

    return BuildResult(
        pages_built=built,
        pages_errors=errors,
        elapsed_seconds=time.time() - t_start,
        errors=sorted(error_lines),
    )


def _canonical_url(page: RenderablePage, project: ProjectConfig) -> str:
    base = project.base_url.rstrip("/")
    path = page.url_path.strip("/")
    return f"{base}/{path}/" if path else f"{base}/"
