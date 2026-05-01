"""Seed the demo database with ZIP code rows from a CSV.

Usage (from the examples/us_zip_codes/ directory):

    python manage.py migrate
    python seed.py                 # loads data/sample_zip_codes.csv
    python seed.py path/to/zips.csv

The CSV must have header row: `zip,city,state,county` (county optional).
"""

import csv
import os
import sys
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    import django

    django.setup()

    from programmatic_pages.models import Page

    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "data" / "sample_zip_codes.csv"
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    with csv_path.open() as f:
        rows = list(csv.DictReader(f))

    print(f"Reading {len(rows):,} rows from {csv_path}")
    Page.objects.filter(project_key="us_zip_codes").delete()

    pages = []
    for row in rows:
        zip_code = row["zip"].strip()
        city = row["city"].strip()
        state = row["state"].strip().upper()
        county = (row.get("county") or "").strip()

        county_clause = (
            f"It's part of {county} County, {state}." if county else f"It's located in {state}."
        )

        pages.append(
            Page(
                project_key="us_zip_codes",
                entity_type="zip-codes",
                url_path=f"zip/{zip_code}/",
                title=f"ZIP {zip_code} — {city}, {state}",
                meta_description=(
                    f"ZIP code {zip_code} covers {city}, {state}. "
                    f"Demographic and locality data for ZCTA {zip_code}."
                ),
                h1=f"ZIP Code {zip_code}",
                body_html=(
                    f"<p>ZIP code <strong>{zip_code}</strong> serves the "
                    f"<strong>{city}, {state}</strong> area. {county_clause}</p>"
                    f"<h2>Quick facts</h2>"
                    f"<table>"
                    f"<tr><th>ZIP code</th><td>{zip_code}</td></tr>"
                    f"<tr><th>City</th><td>{city}</td></tr>"
                    f"<tr><th>State</th><td>{state}</td></tr>"
                    + (f"<tr><th>County</th><td>{county}</td></tr>" if county else "")
                    + "</table>"
                ),
                schema_type="Place",
                schema_extras={
                    "address": {
                        "@type": "PostalAddress",
                        "postalCode": zip_code,
                        "addressLocality": city,
                        "addressRegion": state,
                        "addressCountry": "US",
                    },
                },
                status="published",
            )
        )

    Page.objects.bulk_create(pages, batch_size=1000)
    print(f"Created {len(pages):,} Page rows for project 'us_zip_codes'")


if __name__ == "__main__":
    main()
