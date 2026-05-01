"""pytest-django configuration."""

import django
from django.conf import settings


def pytest_configure(config):
    if not settings.configured:
        from tests import settings as test_settings  # noqa: F401
    django.setup()
