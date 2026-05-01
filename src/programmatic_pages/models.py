"""Models: PageBuild (run audit) + Page (default model for users without one)."""

from django.db import models


class PageBuild(models.Model):
    """Tracks each static page generation run."""

    STATUS_CHOICES = [
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    project_key = models.CharField(max_length=200, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="running")

    pages_built = models.IntegerField(default=0)
    pages_errors = models.IntegerField(default=0)
    build_time_seconds = models.FloatField(default=0)
    output_dir = models.CharField(max_length=500, blank=True, default="")

    entity_type_filter = models.CharField(max_length=100, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    triggered_by = models.CharField(max_length=50, default="manual")

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Page Build"

    def __str__(self) -> str:
        return f"{self.project_key} — {self.pages_built} pages ({self.status})"


class Page(models.Model):
    """Default page model.

    Use this if you don't have a page model yet. If you do, ignore this and
    write your own `PageAdapter` against it.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    project_key = models.CharField(max_length=200, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True, blank=True, default="")

    url_path = models.CharField(max_length=500)
    title = models.CharField(max_length=300)
    meta_description = models.TextField(blank=True, default="")
    h1 = models.CharField(max_length=300)
    body_html = models.TextField(blank=True, default="")

    schema_type = models.CharField(max_length=100, default="WebPage")
    schema_extras = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("project_key", "url_path")]
        indexes = [
            models.Index(fields=["project_key", "status"]),
            models.Index(fields=["project_key", "entity_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.project_key}{self.url_path}"
