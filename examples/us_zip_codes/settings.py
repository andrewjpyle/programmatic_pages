"""Demo Django settings for the us_zip_codes example."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "demo-only-not-for-production"
DEBUG = True
USE_TZ = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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
    "us_zip_codes": {
        "base_url": os.environ.get("DEMO_BASE_URL", "https://zip.example.com"),
        "site_name": "US ZIP Code Atlas",
        "ga_measurement_id": "",
    },
}
