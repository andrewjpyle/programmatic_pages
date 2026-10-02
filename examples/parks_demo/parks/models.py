"""Your own model. programmatic_pages never imports it; the adapter does."""

from django.db import models


class Park(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    acres = models.PositiveIntegerField()
    trail_miles = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    opened = models.PositiveIntegerField()
    description = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name
