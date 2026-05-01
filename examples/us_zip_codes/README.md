# Demo: US ZIP codes

A working `programmatic_pages` demo. Builds a page-per-ZIP-code static site from a CSV.

The bundled fixture is a small geographically-diverse sample (50 ZIPs across ~45 states). Instructions below show how to expand to the full ~33,000 US ZCTAs from public Census data — that's where the throughput claim earns its keep.

## Run the demo (50 pages, ~1 second)

From this directory:

```bash
# 1. Make sure programmatic_pages is installed in your active env
pip install programmatic_pages
# (or: pip install -e ../.. if you're working from the repo)

# 2. Migrate the demo's SQLite DB
python manage.py migrate

# 3. Load the sample CSV into Page records
python seed.py

# 4. Build static HTML
python manage.py build_static_pages \
    --project us_zip_codes \
    --output-dir ./build
```

You'll get output like:

```
Project: US ZIP Code Atlas (us_zip_codes)
Base URL: https://zip.example.com
Output: ./build
==================================================
  Built 50 pages (0 errors) in 0.0s
  Output: ./build
  Manifest: ./build/manifest.json
  Rate: ~3000 pages/s
  Build ID: 1
```

Open `./build/zip/10001/index.html` in a browser — fully static, fully indexable, with Schema.org JSON-LD for `Place` + a breadcrumb chain.

## Serve it locally to check it out

```bash
python -m http.server 8000 --directory ./build
# Visit http://localhost:8000/zip/10001/
```

## Scale up to the full ~33,000 US ZCTAs

The Census Bureau publishes the [ZCTA Relationship File](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html) and various ZCTA→County crosswalks. For demo purposes, the easiest source is [SimpleMaps' free US ZIP database](https://simplemaps.com/data/us-zips) (CC-BY 4.0). Download `uszips.csv`, then:

```bash
# uszips.csv has many columns; remap to the 4 we want
python -c "
import csv
with open('uszips.csv') as inp, open('full_zips.csv', 'w', newline='') as out:
    r = csv.DictReader(inp)
    w = csv.DictWriter(out, fieldnames=['zip', 'city', 'state', 'county'])
    w.writeheader()
    for row in r:
        w.writerow({
            'zip': row['zip'],
            'city': row['city'],
            'state': row['state_id'],
            'county': row.get('county_name', ''),
        })
"

python seed.py full_zips.csv
python manage.py build_static_pages --project us_zip_codes --output-dir ./build
```

On a recent Mac with `--concurrency 8` you should see 2,000+ pages/sec.

## What this demo demonstrates

- **The bundled `Page` model + `DefaultPageAdapter` works without writing any adapter code.** Useful for quick prototypes and small-to-medium sites.
- **`schema_extras` decorates the JSON-LD per page** with `PostalAddress` here.
- **`entity_type` filtering and breakdowns** — try `python manage.py build_static_pages --project us_zip_codes --dry-run`.
- **`PageBuild` audit log** — every run is recorded. Try a few builds, then `python manage.py shell -c "from programmatic_pages.models import PageBuild; [print(b) for b in PageBuild.objects.all()]"`.

## Next: write your own adapter

For any real project you'll have your own Django model — say `Listing`, `Product`, `Profile` — and you don't want to migrate to ours. See the [adapter pattern walkthrough](../../README.md#the-adapter-pattern-when-you-have-your-own-model) in the main README.
