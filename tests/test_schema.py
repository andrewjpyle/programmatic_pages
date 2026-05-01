"""Tests for the JSON-LD schema builder. Pure data, no DB."""

import json

from programmatic_pages.adapter import BreadcrumbItem, ProjectConfig, RenderablePage
from programmatic_pages.schema import build_schema_json


def _project() -> ProjectConfig:
    return ProjectConfig(base_url="https://example.com", site_name="Example")


def test_minimal_page_yields_single_block():
    page = RenderablePage(
        url_path="hello/",
        title="Hello",
        meta_description="Hi",
        h1="Hello",
        body_html="<p>Hi</p>",
    )
    blocks = json.loads(build_schema_json(page, _project()))
    assert len(blocks) == 1
    assert blocks[0]["@type"] == "WebPage"
    assert blocks[0]["url"] == "https://example.com/hello/"
    assert blocks[0]["name"] == "Hello"


def test_schema_extras_merge_into_primary():
    page = RenderablePage(
        url_path="people/jane/",
        title="Jane",
        meta_description="A person",
        h1="Jane Doe",
        body_html="",
        schema_type="Person",
        schema_extras={
            "jobTitle": "Engineer",
            "affiliation": {"@type": "Organization", "name": "Acme"},
        },
    )
    primary = json.loads(build_schema_json(page, _project()))[0]
    assert primary["@type"] == "Person"
    assert primary["jobTitle"] == "Engineer"
    assert primary["affiliation"]["name"] == "Acme"


def test_breadcrumbs_render_with_relative_urls_resolved():
    page = RenderablePage(
        url_path="people/jane/",
        title="Jane",
        meta_description="",
        h1="Jane Doe",
        body_html="",
        breadcrumb_chain=[
            BreadcrumbItem(label="Home", url="/"),
            BreadcrumbItem(label="People", url="/people/"),
            BreadcrumbItem(label="Jane Doe"),  # no url = current page
        ],
    )
    blocks = json.loads(build_schema_json(page, _project()))
    assert len(blocks) == 2
    crumbs = blocks[1]["itemListElement"]
    assert len(crumbs) == 3
    assert crumbs[0]["item"] == "https://example.com/"
    assert crumbs[1]["item"] == "https://example.com/people/"
    assert "item" not in crumbs[2]
    assert crumbs[2]["name"] == "Jane Doe"


def test_breadcrumbs_with_absolute_url_left_alone():
    page = RenderablePage(
        url_path="x/",
        title="X",
        meta_description="",
        h1="X",
        body_html="",
        breadcrumb_chain=[BreadcrumbItem(label="Other", url="https://other.example.com/")],
    )
    crumbs = json.loads(build_schema_json(page, _project()))[1]["itemListElement"]
    assert crumbs[0]["item"] == "https://other.example.com/"


def test_root_url_path_renders_canonical_correctly():
    page = RenderablePage(
        url_path="",
        title="Home",
        meta_description="",
        h1="Welcome",
        body_html="",
    )
    primary = json.loads(build_schema_json(page, _project()))[0]
    assert primary["url"] == "https://example.com/"
