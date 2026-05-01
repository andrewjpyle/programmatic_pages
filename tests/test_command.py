"""End-to-end test: bundled Page model + DefaultPageAdapter + mgmt command."""


import pytest
from django.core.management import call_command


@pytest.fixture
def populated_pages(db):
    from programmatic_pages.models import Page

    Page.objects.create(
        project_key="demo",
        entity_type="zip-codes",
        url_path="zip/00501/",
        title="ZIP 00501 — Holtsville, NY",
        meta_description="ZIP code 00501 covers Holtsville, NY.",
        h1="ZIP 00501",
        body_html="<p>Holtsville, NY 00501.</p>",
        schema_type="Place",
        status="published",
    )
    Page.objects.create(
        project_key="demo",
        entity_type="zip-codes",
        url_path="zip/10001/",
        title="ZIP 10001 — New York, NY",
        meta_description="ZIP code 10001 covers New York, NY.",
        h1="ZIP 10001",
        body_html="<p>New York, NY 10001.</p>",
        schema_type="Place",
        status="published",
    )
    Page.objects.create(
        project_key="demo",
        entity_type="zip-codes",
        url_path="zip/draft/",
        title="Draft",
        meta_description="",
        h1="Draft",
        body_html="",
        status="draft",
    )


def test_dry_run_counts_published(populated_pages, capsys, tmp_path):
    call_command(
        "build_static_pages",
        "--project", "demo",
        "--dry-run",
        "--output-dir", str(tmp_path),
    )
    out = capsys.readouterr().out
    assert "Pages matching filters: 2" in out
    assert "DRY RUN" in out
    assert not (tmp_path / "manifest.json").exists()


def test_full_build_writes_files_and_manifest(populated_pages, tmp_path):
    call_command(
        "build_static_pages",
        "--project", "demo",
        "--output-dir", str(tmp_path),
        "--concurrency", "1",
    )
    assert (tmp_path / "zip" / "00501" / "index.html").is_file()
    assert (tmp_path / "zip" / "10001" / "index.html").is_file()
    # Draft page should NOT be built (default status filter is 'published')
    assert not (tmp_path / "zip" / "draft" / "index.html").exists()
    assert (tmp_path / "manifest.json").is_file()


def test_built_html_contains_canonical_and_schema(populated_pages, tmp_path):
    call_command(
        "build_static_pages",
        "--project", "demo",
        "--output-dir", str(tmp_path),
        "--concurrency", "1",
    )
    html = (tmp_path / "zip" / "00501" / "index.html").read_text()
    assert 'rel="canonical"' in html
    assert "https://demo.example.com/zip/00501/" in html
    assert "ZIP 00501" in html
    assert '"@type": "Place"' in html or '"@type":"Place"' in html


def test_entity_type_filter_works(populated_pages, tmp_path):
    from programmatic_pages.models import Page

    Page.objects.create(
        project_key="demo",
        entity_type="other",
        url_path="other/x/",
        title="X",
        meta_description="",
        h1="X",
        body_html="",
        status="published",
    )

    call_command(
        "build_static_pages",
        "--project", "demo",
        "--entity-type", "zip-codes",
        "--output-dir", str(tmp_path),
        "--concurrency", "1",
    )
    assert (tmp_path / "zip" / "00501" / "index.html").is_file()
    assert not (tmp_path / "other" / "x" / "index.html").exists()


def test_pagebuild_record_created(populated_pages, tmp_path, db):
    from programmatic_pages.models import PageBuild

    before = PageBuild.objects.count()
    call_command(
        "build_static_pages",
        "--project", "demo",
        "--output-dir", str(tmp_path),
        "--concurrency", "1",
    )
    assert PageBuild.objects.count() == before + 1
    record = PageBuild.objects.latest("started_at")
    assert record.status == "completed"
    assert record.pages_built == 2
    assert record.pages_errors == 0
    assert record.finished_at is not None
