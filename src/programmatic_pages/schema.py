"""Schema.org JSON-LD builder. Pure data, no Django imports."""

import json

from programmatic_pages.adapter import ProjectConfig, RenderablePage

# The payload is inlined into a <script> element, where the HTML parser ends the element at the
# first "</script" no matter what JSON thinks. Escaping <, > and & as JSON unicode escapes keeps
# the payload valid JSON with identical values, and makes a breakout impossible. Same approach as
# Django's json_script filter.
_SCRIPT_SAFE = str.maketrans({"<": "\\u003c", ">": "\\u003e", "&": "\\u0026"})


def build_schema_json(page: RenderablePage, project: ProjectConfig) -> str:
    """Build a JSON-LD payload for a page.

    Returns a JSON string containing a list with the primary entity schema and
    a BreadcrumbList. The string is safe to inline inside <script type="application/ld+json">:
    <, > and & are written as unicode escapes, so user text cannot close the element.

    The primary schema starts from `page.schema_type` plus `page.schema_extras`, so callers
    can decorate any schema.org type freely.
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

    return json.dumps(blocks, ensure_ascii=False).translate(_SCRIPT_SAFE)


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
