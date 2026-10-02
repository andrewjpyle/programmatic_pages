# Demo: Example County Parks (your own model + an adapter)

> **SAMPLE DATA.** Every park, town, acreage and date in `data/parks.csv` is fictional.

This demo is the realistic case: you already have a Django model (`parks.Park`) and you do not
want to copy it into the bundled `Page` table. One adapter class (`parks/adapters.py`) turns each
eligible `Park` row into a page.

Seven parks are in the CSV. Two of them have no description and no trail data, so the adapter's
queryset leaves them out and they get **no page**. A page for them would be a name and a number.

## Run it

From the repo root:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
cd examples/parks_demo
python manage.py migrate
python seed.py
python manage.py build_static_pages --project parks \
    --adapter parks.adapters.ParkPageAdapter --output-dir ./build
python check_build.py ./build
```

`check_build.py` reads the output the way a crawler would: one page per eligible park, exactly one
`ld+json` script per page that parses as JSON, and a canonical URL equal to the JSON-LD `url` and to
the address the file is served from. It exits 1 on any miss. CI runs this demo on every push.

## What a real run produced

Committed in [`output/`](output/), copied from the captures that also drive the README graphics:

- [`output/build_output.txt`](output/build_output.txt): the build command's output.
- [`output/check_output.txt`](output/check_output.txt): the checker's verdict for all 7 parks.
- [`output/fox-and-heron.head.html`](output/fox-and-heron.head.html): the generated `<head>` for
  "Fox & Heron Commons", whose name and description carry an `&` and quotes. They are escaped once
  in the HTML attributes and written as `&` inside the JSON-LD.

## Files

| File | What it is |
|---|---|
| `parks/models.py` | The model you already have. `programmatic_pages` never imports it. |
| `parks/adapters.py` | The integration: which parks get a page, and what each page says. |
| `data/parks.csv` | 7 fictional parks. |
| `seed.py` | Loads the CSV. |
| `check_build.py` | Verifies the build output. |
