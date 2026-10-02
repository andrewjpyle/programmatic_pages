# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **JSON-LD script breakout.** A title or description containing `</script>` closed the
  `ld+json` element and could inject a script. `<`, `>` and `&` are now written as unicode escapes.
- **Double-escaped meta description.** Quotes rendered as `&amp;quot;` in the description, Open
  Graph and Twitter tags. They are now escaped once.
- **Path traversal.** A `url_path` such as `../x/` wrote outside `--output-dir`. It is now refused
  and reported as a failed page.
- **Duplicate `url_path`.** A second page with the same path overwrote the first and was counted as
  built. It is now reported as a failed page.

### Changed
- `build_static_pages` exits 1 when any page fails, prints each failure as `url_path: reason`, and
  stores them on the `PageBuild` row. `BuildResult` has a new `errors` list.
- README quickstart installs from a checkout (the package is not on PyPI yet).

### Added
- `examples/parks_demo/`: a custom model and adapter over 7 fictional parks, with `check_build.py`.
- `examples/hostile_record.py` and `tests/test_safety.py` (27 tests in total).
- CI: a test-count floor, `pipefail` on piped steps, Django 5.2, and the parks demo on every run.

## [0.1.0.dev0] (initial scaffold)

The first cut. Alpha: the API surface is settling and may shift before 0.1.0.

### Added
- **`PageAdapter` contract** with `RenderablePage`, `ProjectConfig`, and `BreadcrumbItem` dataclasses.
- **`DefaultPageAdapter`** that works against the bundled `Page` model, so you can `pip install` and have a working tool without writing an adapter.
- **`Page` model** for users without their own page model.
- **`PageBuild` model** as a per-run audit log (status, count, errors, runtime, output dir).
- **`build_static_pages` management command** with `--project`, `--adapter`, `--template`, `--output-dir`, `--entity-type`, `--status`, `--limit`, `--concurrency`, `--dry-run`, `--triggered-by`.
- **Parallel render+write loop** via `ThreadPoolExecutor`.
- **Schema.org JSON-LD generator** with pluggable `schema_type` and free-form `schema_extras`.
- **N-level breadcrumb chain** rendered to both HTML and `BreadcrumbList` JSON-LD.
- **Build manifest** (`manifest.json`) emitted alongside output.
- **Default Django template** with HTML5 + OG + Twitter card + JSON-LD slot + responsive CSS + optional GA4 snippet.
- **Reference demo** (`examples/us_zip_codes/`): runnable in three commands; bundled 50-row CSV scales to ~33K Census ZCTAs via SimpleMaps.
- **Test suite**: 17 tests covering schema, manifest, builder, and the end-to-end management command path.
- **CI workflow**: Python 3.10/3.11/3.12 × Django 4.2/5.0/5.1 matrix on GitHub Actions.

[Unreleased]: https://github.com/andrewjpyle/programmatic_pages/compare/v0.1.0.dev0...HEAD
[0.1.0.dev0]: https://github.com/andrewjpyle/programmatic_pages/releases/tag/v0.1.0.dev0
