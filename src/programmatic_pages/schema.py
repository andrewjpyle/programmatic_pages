"""Schema.org JSON-LD builder. Pure data, no Django imports."""

import json

from programmatic_pages.adapter import ProjectConfig, RenderablePage


def build_schema_json(page: RenderablePage, project: ProjectConfig) -> str:
    """Build a JSON-LD payload for a page.

    Returns a JSON string containing a list with the primary entity schema and
    a BreadcrumbList. The primary schema starts from `page.schema_type` plus
    `page.schema_extras`, so callers can decorate any schema.org type freely.
    """
    canonical_url = _canonical_url(page, project)

    primary = {
        "@context": "https://schema.org",
        "@type": page.schema_type,
        "name": page.h1 or page.title,
        "url": canonical_url,
        "description": page.meta_description,
    }
    if page.schema_extras:
        primary.update(page.schema_extras)

    blocks: list[dict] = [primary]

    if page.breadcrumb_chain:
        blocks.append(_breadcrumb_block(page, project))

    return json.dumps(blocks, ensure_ascii=False)


def _canonical_url(page: RenderablePage, project: ProjectConfig) -> str:
    base = project.base_url.rstrip("/")
    path = page.url_path.strip("/")
    return f"{base}/{path}/" if path else f"{base}/"


def _breadcrumb_block(page: RenderablePage, project: ProjectConfig) -> dict:
    base = project.base_url.rstrip("/")
    items = []
    for position, crumb in enumerate(page.breadcrumb_chain, start=1):
        item: dict = {
            "@type": "ListItem",
            "position": position,
            "name": crumb.label,
        }
        if crumb.url is not None:
            url = crumb.url
            if url.startswith("/"):
                url = f"{base}{url}"
            item["item"] = url
        items.append(item)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
