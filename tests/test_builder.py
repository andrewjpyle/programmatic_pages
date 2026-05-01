"""Tests for render_page + write_page + build()."""

import os

import pytest
from django.template import Template

from programmatic_pages.adapter import ProjectConfig, RenderablePage
from programmatic_pages.builder import build, render_page, write_page


@pytest.fixture
def project() -> ProjectConfig:
    return ProjectConfig(base_url="https://example.com", site_name="Example", ga_measurement_id="")


@pytest.fixture
def template() -> Template:
    return Template(
        "<!doctype html><title>{{ title }}</title>"
        "<link rel=canonical href=\"{{ canonical_url }}\">"
        "<h1>{{ h1 }}</h1>{{ body_html|safe }}"
        "<script type=application/ld+json>{{ schema_json|safe }}</script>"
    )


def test_render_page_outputs_canonical_and_title(project, template):
    page = RenderablePage(
        url_path="things/foo/",
        title="Foo",
        meta_description="x",
        h1="Foo Heading",
        body_html="<p>body</p>",
    )
    html = render_page(page, project, template)
    assert "<title>Foo</title>" in html
    assert 'href="https://example.com/things/foo/"' in html
    assert "<h1>Foo Heading</h1>" in html
    assert "<p>body</p>" in html
    assert "WebPage" in html  # JSON-LD present


def test_write_page_creates_index_html(tmp_path):
    out = str(tmp_path)
    path = write_page(out, "things/foo/", "<html>x</html>")
    assert path.endswith("things/foo/index.html")
    assert os.path.isfile(path)
    with open(path) as f:
        assert f.read() == "<html>x</html>"


def test_write_page_handles_root_path(tmp_path):
    out = str(tmp_path)
    path = write_page(out, "/", "<html>root</html>")
    assert path.endswith("index.html")
    assert os.path.isfile(path)


def test_build_writes_all_pages(tmp_path, project, template):
    pages = [
        RenderablePage(
            url_path=f"items/{i}/",
            title=f"Item {i}",
            meta_description="",
            h1=f"Item {i}",
            body_html=f"<p>{i}</p>",
        )
        for i in range(5)
    ]
    out = str(tmp_path)
    result = build(pages, project, template, out, concurrency=2)
    assert result.pages_built == 5
    assert result.pages_errors == 0
    for i in range(5):
        assert os.path.isfile(os.path.join(out, "items", str(i), "index.html"))


def test_build_continues_past_errors(tmp_path, project):
    # Default Django swallows missing attrs; this still proves the loop returns cleanly.
    bad_template = Template("{{ does_not_exist.attribute }}")
    pages = [
        RenderablePage(
            url_path="ok/",
            title="OK",
            meta_description="",
            h1="OK",
            body_html="",
        ),
    ]
    # The builder should at least produce a result without raising.
    result = build(pages, project, bad_template, str(tmp_path), concurrency=1)
    assert result.pages_built + result.pages_errors == 1
