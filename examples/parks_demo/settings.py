"""Settings for the parks demo. SAMPLE DATA: every park, town and number here is fictional."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "demo-only-not-for-production"
DEBUG = True
USE_TZ = True

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "programmatic_pages",
    "parks",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    }
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

PARKS_SITE = {"base_url": "https://parks.example.com", "site_name": "Example County Parks"}
