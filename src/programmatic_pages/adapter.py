"""Adapter contract — implement against your own page model, or use the default."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class BreadcrumbItem:
    label: str
    url: str | None = None  # None for the current page (last item, no link)


@dataclass
class RenderablePage:
    """A flat, framework-agnostic page record passed to the renderer.

    The adapter's job is to turn whatever model you have into one of these.
    """

    url_path: str
    title: str
    meta_description: str
    h1: str
    body_html: str
    schema_type: str = "WebPage"
    schema_extras: dict = field(default_factory=dict)
    breadcrumb_chain: list[BreadcrumbItem] = field(default_factory=list)
    # Free-form bag for template authors who add their own variables.
    extra_context: dict = field(default_factory=dict)


@dataclass
class ProjectConfig:
    """Per-project configuration the renderer needs."""

    base_url: str
    site_name: str
    ga_measurement_id: str = ""


class PageAdapter(ABC):
    """Implement against your own page model.

    For users without an existing model, see `programmatic_pages.adapters.DefaultPageAdapter`
    which works against the bundled `Page` model.
    """

    @abstractmethod
    def get_project_config(self, project_key: str) -> ProjectConfig:
        """Return base_url, site_name, GA id, etc. for the project."""

    @abstractmethod
    def iter_pages(
        self,
        project_key: str,
        *,
        entity_type: str | None = None,
        status: str = "published",
    ) -> Iterable[RenderablePage]:
        """Yield RenderablePage instances matching the filters."""

    def get_breakdown(
        self,
        project_key: str,
        *,
        status: str = "published",
    ) -> dict[str, int]:
        """Optional. Return counts grouped by entity_type for --dry-run output.

        Default implementation just returns the total count.
        """
        return {"total": sum(1 for _ in self.iter_pages(project_key, status=status))}
