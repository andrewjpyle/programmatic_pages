"""ParkPageAdapter: turns Park rows into RenderablePage records.

This is the whole integration. The rule for which parks get a page lives here, in the
queryset, so `build_static_pages --dry-run` reports the same number the build will write.
"""

from collections.abc import Iterable

from django.conf import settings
from django.db.models import Count
from django.utils.html import escape

from parks.models import Park
from programmatic_pages import BreadcrumbItem, PageAdapter, ProjectConfig, RenderablePage


def _eligible():
    # A park earns a page only when it has a description and trail data. The other rows are
    # real records too, but a page for them would be a name and a number: thin, so no page.
    return Park.objects.exclude(description="").exclude(trail_miles=None)


class ParkPageAdapter(PageAdapter):
    def get_project_config(self, project_key: str) -> ProjectConfig:
        return ProjectConfig(**settings.PARKS_SITE)

    def iter_pages(
        self, project_key: str, *, entity_type: str | None = None, status: str = "published"
    ) -> Iterable[RenderablePage]:
        for park in _eligible().order_by("slug").iterator():
            yield RenderablePage(
                url_path=f"parks/{park.slug}/",
                title=f"{park.name}, {park.city}: trails, size and history",
                meta_description=park.description,
                h1=park.name,
                body_html=(
                    f"<p>{escape(park.description)}</p>"
                    "<table>"
                    f"<tr><th>Town</th><td>{escape(park.city)}</td></tr>"
                    f"<tr><th>Size</th><td>{park.acres} acres</td></tr>"
                    f"<tr><th>Trails</th><td>{park.trail_miles} miles</td></tr>"
                    f"<tr><th>Opened</th><td>{park.opened}</td></tr>"
                    "</table>"
                ),
                schema_type="Park",
                schema_extras={
                    "address": {"@type": "PostalAddress", "addressLocality": park.city},
                    "foundingDate": str(park.opened),
                },
                breadcrumb_chain=[
                    BreadcrumbItem(label="Home", url="/"),
                    BreadcrumbItem(label="Parks", url="/parks/"),
                    BreadcrumbItem(label=park.name),
                ],
            )

    def get_breakdown(self, project_key: str, *, status: str = "published") -> dict[str, int]:
        rows = _eligible().values("city").annotate(c=Count("id"))
        return {row["city"]: row["c"] for row in rows}
