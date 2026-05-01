"""programmatic_pages — generate SEO-quality static pages from a Django queryset."""

from programmatic_pages.adapter import (
    BreadcrumbItem,
    PageAdapter,
    ProjectConfig,
    RenderablePage,
)

__all__ = [
    "BreadcrumbItem",
    "PageAdapter",
    "ProjectConfig",
    "RenderablePage",
]

__version__ = "0.1.0.dev0"

default_app_config = "programmatic_pages.apps.ProgrammaticPagesConfig"
