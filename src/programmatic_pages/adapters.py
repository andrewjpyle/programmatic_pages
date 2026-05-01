"""Default adapter — implements PageAdapter against the bundled `Page` model.

Use this if you don't have your own page model. If you do, write your own
adapter against your model and pass `--adapter` to the management command.
"""

from collections.abc import Iterable

from programmatic_pages.adapter import (
    BreadcrumbItem,
    PageAdapter,
    ProjectConfig,
    RenderablePage,
)


class DefaultPageAdapter(PageAdapter):
    """Adapter for the bundled `programmatic_pages.models.Page` model.

    Project configuration is sourced from Django settings:

        PROGRAMMATIC_PAGES = {
            "myproject": {
                "base_url": "https://example.com",
                "site_name": "Example",
                "ga_measurement_id": "G-XXXXXXXXXX",  # optional
            },
        }
    """

    def get_project_config(self, project_key: str) -> ProjectConfig:
        from django.conf import settings

        config = getattr(settings, "PROGRAMMATIC_PAGES", {}).get(project_key, {})
        if not config:
            raise ValueError(
                f"No PROGRAMMATIC_PAGES config for project '{project_key}'. "
                f"Add it to settings.py or write a custom PageAdapter."
            )
        return ProjectConfig(
            base_url=config["base_url"],
            site_name=config["site_name"],
            ga_measurement_id=config.get("ga_measurement_id", ""),
        )

    def iter_pages(
        self,
        project_key: str,
        *,
        entity_type: str | None = None,
        status: str = "published",
    ) -> Iterable[RenderablePage]:
        from programmatic_pages.models import Page

        qs = Page.objects.filter(project_key=project_key, status=status)
        if entity_type:
            qs = qs.filter(entity_type=entity_type)

        for page in qs.iterator():
            yield RenderablePage(
                url_path=page.url_path,
                title=page.title,
                meta_description=page.meta_description,
                h1=page.h1,
                body_html=page.body_html,
                schema_type=page.schema_type or "WebPage",
                schema_extras=page.schema_extras or {},
                breadcrumb_chain=self._default_breadcrumbs(page),
            )

    def get_breakdown(
        self,
        project_key: str,
        *,
        status: str = "published",
    ) -> dict[str, int]:
        from django.db.models import Count

        from programmatic_pages.models import Page

        rows = (
            Page.objects.filter(project_key=project_key, status=status)
            .values("entity_type")
            .annotate(c=Count("id"))
            .order_by("-c")
        )
        return {row["entity_type"] or "(none)": row["c"] for row in rows}

    @staticmethod
    def _default_breadcrumbs(page) -> list[BreadcrumbItem]:
        chain = [BreadcrumbItem(label="Home", url="/")]
        if page.entity_type:
            label = page.entity_type.replace("-", " ").replace("_", " ").title()
            chain.append(BreadcrumbItem(label=label, url=f"/{page.entity_type}/"))
        chain.append(BreadcrumbItem(label=page.h1 or page.title))
        return chain
