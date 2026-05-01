"""Minimal Django settings for the test suite."""

SECRET_KEY = "test-key-not-secret"
DEBUG = True
USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "programmatic_pages",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    }
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

PROGRAMMATIC_PAGES = {
    "demo": {
        "base_url": "https://demo.example.com",
        "site_name": "Demo Site",
        "ga_measurement_id": "",
    },
}
