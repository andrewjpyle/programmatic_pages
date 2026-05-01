"""Tests for the manifest writer."""

import json
import os

from programmatic_pages.manifest import write_manifest


def test_manifest_written_with_required_fields(tmp_path):
    path = write_manifest(
        str(tmp_path),
        project_key="demo",
        base_url="https://demo.example.com",
        pages_built=42,
        pages_errors=0,
        build_time_seconds=1.234,
    )
    assert os.path.basename(path) == "manifest.json"
    with open(path) as f:
        data = json.load(f)
    assert data["project_key"] == "demo"
    assert data["pages_built"] == 42
    assert data["pages_errors"] == 0
    assert data["build_time_seconds"] == 1.2  # rounded to 1 decimal
    assert "built_at" in data
    assert data["built_at"].endswith("Z")


def test_manifest_extra_fields_merged(tmp_path):
    write_manifest(
        str(tmp_path),
        project_key="demo",
        base_url="https://x.com",
        pages_built=1,
        pages_errors=0,
        build_time_seconds=0.1,
        extra={"git_sha": "abc123", "deployed_to": "/var/www/x"},
    )
    with open(tmp_path / "manifest.json") as f:
        data = json.load(f)
    assert data["git_sha"] == "abc123"
    assert data["deployed_to"] == "/var/www/x"
