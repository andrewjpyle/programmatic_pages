"""Build static HTML pages for a project.

Usage:
    manage.py build_static_pages --project myproject
    manage.py build_static_pages --project myproject --limit 10
    manage.py build_static_pages --project myproject --entity-type zip-codes
    manage.py build_static_pages --project myproject --dry-run
    manage.py build_static_pages --project myproject --output-dir /tmp/build
    manage.py build_static_pages --project myproject \\
        --adapter myapp.adapters.MyPageAdapter
    manage.py build_static_pages --project myproject \\
        --template myapp/custom_template.html
"""

import importlib
import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.template import Template
from django.template.loader import get_template

from programmatic_pages.adapter import PageAdapter
from programmatic_pages.builder import build
from programmatic_pages.manifest import write_manifest


DEFAULT_ADAPTER = "programmatic_pages.adapters.DefaultPageAdapter"
DEFAULT_TEMPLATE = "programmatic_pages/default.html"
DEFAULT_OUTPUT_BASE = "~/programmatic_pages/build"


class Command(BaseCommand):
    help = "Build static HTML pages for a project."

    def add_arguments(self, parser):
        parser.add_argument("--project", required=True, help="Project key")
        parser.add_argument(
            "--adapter",
            default=DEFAULT_ADAPTER,
            help=f"Dotted import path to a PageAdapter (default: {DEFAULT_ADAPTER})",
        )
        parser.add_argument(
            "--template",
            default=DEFAULT_TEMPLATE,
            help=f"Template name or path (default: {DEFAULT_TEMPLATE})",
        )
        parser.add_argument(
            "--output-dir",
            default="",
            help=f"Output directory (default: {DEFAULT_OUTPUT_BASE}/<project>)",
        )
        parser.add_argument("--limit", type=int, default=0, help="Max pages (0=all)")
        parser.add_argument("--entity-type", default=None, help="Filter by entity_type")
        parser.add_argument("--status", default="published", help="Filter by status")
        parser.add_argument("--concurrency", type=int, default=4)
        parser.add_argument("--dry-run", action="store_true", help="Count, don't build")
        parser.add_argument("--triggered-by", default="manual")

    def handle(self, *args, **options):
        from django.utils import timezone as tz

        from programmatic_pages.models import PageBuild

        project_key = options["project"]
        adapter = _load_adapter(options["adapter"])
        project = adapter.get_project_config(project_key)

        output_dir = options["output_dir"] or os.path.expanduser(
            f"{DEFAULT_OUTPUT_BASE}/{project_key}"
        )

        self.stdout.write(f"\nProject: {project.site_name} ({project_key})")
        self.stdout.write(f"Base URL: {project.base_url}")
        self.stdout.write(f"Output: {output_dir}")

        if options["dry_run"]:
            breakdown = adapter.get_breakdown(project_key, status=options["status"])
            total = sum(breakdown.values())
            self.stdout.write(f"\nPages matching filters: {total:,}")
            if breakdown and set(breakdown) != {"total"}:
                self.stdout.write("\nBreakdown:")
                for label, count in sorted(breakdown.items(), key=lambda kv: -kv[1]):
                    self.stdout.write(f"  {label}: {count:,}")
            self.stdout.write(self.style.WARNING("\nDRY RUN — no files written"))
            return

        # Resolve pages stream + apply limit
        pages = adapter.iter_pages(
            project_key,
            entity_type=options["entity_type"],
            status=options["status"],
        )
        if options["limit"]:
            pages = _take(pages, options["limit"])

        # Resolve template
        template = _load_template(options["template"])

        # Create build record
        record = PageBuild.objects.create(
            project_key=project_key,
            status="running",
            output_dir=output_dir,
            entity_type_filter=options["entity_type"] or "",
            triggered_by=options["triggered_by"],
        )

        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            log_interval = 1000

            def _on_progress(done: int, built: int, errors: int, rate: float) -> None:
                self.stdout.write(
                    f"  [{done:,}] built={built:,} errors={errors:,} ({rate:.0f} pages/s)"
                )

            result = build(
                pages,
                project,
                template,
                output_dir,
                concurrency=options["concurrency"],
                on_progress=_on_progress,
                log_interval=log_interval,
            )

            manifest_path = write_manifest(
                output_dir,
                project_key=project_key,
                base_url=project.base_url,
                pages_built=result.pages_built,
                pages_errors=result.pages_errors,
                build_time_seconds=result.elapsed_seconds,
                entity_type_filter=options["entity_type"],
            )

            record.status = "completed" if result.pages_errors == 0 else "failed"
            record.pages_built = result.pages_built
            record.pages_errors = result.pages_errors
            record.build_time_seconds = round(result.elapsed_seconds, 1)
            record.finished_at = tz.now()
            if result.pages_errors > 0:
                record.error_message = f"{result.pages_errors} pages failed to build"
            record.save()

            rate = (
                result.pages_built / result.elapsed_seconds
                if result.elapsed_seconds > 0
                else 0
            )
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Built {result.pages_built:,} pages "
                    f"({result.pages_errors:,} errors) in {result.elapsed_seconds:.1f}s\n"
                    f"  Output: {output_dir}\n"
                    f"  Manifest: {manifest_path}\n"
                    f"  Rate: {rate:.0f} pages/s\n"
                    f"  Build ID: {record.id}"
                )
            )
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            record.finished_at = tz.now()
            record.save()
            raise


def _load_adapter(dotted_path: str) -> PageAdapter:
    module_path, _, attr = dotted_path.rpartition(".")
    if not module_path:
        raise ValueError(f"Invalid adapter path: {dotted_path}")
    module = importlib.import_module(module_path)
    cls = getattr(module, attr)
    return cls()


def _load_template(name_or_path: str) -> Template:
    """Resolve template via Django loader, or read from disk if it looks like a path."""
    if os.path.exists(name_or_path):
        with open(name_or_path, encoding="utf-8") as f:
            return Template(f.read())
    return get_template(name_or_path).template


def _take(it, n: int):
    """Yield up to n items from an iterable."""
    for i, item in enumerate(it):
        if i >= n:
            return
        yield item
