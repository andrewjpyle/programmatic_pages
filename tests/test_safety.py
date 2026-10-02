"""Escaping and filesystem safety: what a hostile or sloppy record can and cannot do.

Every page is built from data you may not fully control (scraped names, user-submitted titles).
These tests pin the guarantees the README makes about that data.
"""

import json
from html.parser import HTMLParser

import pytest
from django.template.loader import get_template

from programmatic_pages.adapter import BreadcrumbItem, ProjectConfig, RenderablePage
from programmatic_pages.builder import build, render_page, write_page
from programmatic_pages.schema import build_schema_json

HOSTILE = 'Evil </script><script>alert(1)</script> & "quoted"'


class _Head(HTMLParser):
    """Collects what a browser's parser would see: ld+json scripts, meta tags, canonical."""

    def __init__(self):
        super().__init__()
        self.scripts: list[dict] = []
        self.metas: dict[str, str] = {}
        self.canonical: str | None = None
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            self._in = {"type": a.get("type"), "data": ""}
            self.scripts.append(self._in)
        elif tag == "meta" and "name" in a:
            self.metas[a["name"]] = a.get("content")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")

    def handle_endtag(self, tag):
        if tag == "script":
            self._in = None

    def handle_data(self, data):
        if self._in is not None:
            self._in["data"] += data


def _default_template():
    return get_template("programmatic_pages/default.html").template


def _project() -> ProjectConfig:
    return ProjectConfig(base_url="https://parks.example.com", site_name="Example Parks")


def _hostile_page() -> RenderablePage:
    return RenderablePage(
        url_path="parks/evil/",
        title=HOSTILE,
        meta_description=HOSTILE,
        h1=HOSTILE,
        body_html="<p>trusted body</p>",
        schema_type="Park",
        breadcrumb_chain=[BreadcrumbItem(label="Home", url="/"), BreadcrumbItem(label=HOSTILE)],
    )


def test_jsonld_string_cannot_close_its_script_element():
    payload = build_schema_json(_hostile_page(), _project())
    assert "</" not in payload
    assert "<" not in payload and ">" not in payload
    blocks = json.loads(payload)
    assert blocks[0]["name"] == HOSTILE  # same value after parsing, only the encoding changed
    assert blocks[1]["itemListElement"][1]["name"] == HOSTILE


def test_rendered_page_has_exactly_one_parseable_jsonld_script():
    html = render_page(_hostile_page(), _project(), _default_template())
    head = _Head()
    head.feed(html)
    ld = [s for s in head.scripts if s["type"] == "application/ld+json"]
    assert len(ld) == 1
    assert len(head.scripts) == 1  # no injected <script> element appeared
    assert json.loads(ld[0]["data"])[0]["name"] == HOSTILE


def test_meta_description_is_escaped_exactly_once():
    page = RenderablePage(
        url_path="parks/maple/",
        title="Maple",
        meta_description='A "quiet" park & lake.',
        h1="Maple",
        body_html="",
    )
    html = render_page(page, _project(), _default_template())
    assert 'content="A &quot;quiet&quot; park &amp; lake."' in html
    assert "&amp;quot;" not in html
    head = _Head()
    head.feed(html)
    assert head.metas["description"] == 'A "quiet" park & lake.'
    assert head.canonical == "https://parks.example.com/parks/maple/"


@pytest.mark.parametrize("bad", ["../x/", "a/../../x/", "/../x", ".."])
def test_write_page_refuses_paths_outside_output_dir(tmp_path, bad):
    out = tmp_path / "build"
    out.mkdir()
    with pytest.raises(ValueError, match="outside the output directory"):
        write_page(str(out), bad, "<html></html>")
    assert list(tmp_path.iterdir()) == [out]
    assert list(out.iterdir()) == []


def test_duplicate_url_path_is_an_error_not_a_silent_overwrite(tmp_path):
    from django.template import Template

    pages = [
        RenderablePage(
            url_path="parks/a/", title="First", meta_description="", h1="", body_html=""
        ),
        RenderablePage(
            url_path="/parks/a", title="Second", meta_description="", h1="", body_html=""
        ),
    ]
    result = build(pages, _project(), Template("{{ title }}"), str(tmp_path), concurrency=1)
    assert result.pages_built == 1
    assert result.pages_errors == 1
    assert "duplicate url_path" in result.errors[0]
    assert (tmp_path / "parks" / "a" / "index.html").read_text() == "First"
