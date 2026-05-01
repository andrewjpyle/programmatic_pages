# programmatic_pages

> Generate millions of SEO-quality static pages from a Django queryset, at thousands per second.

[![Tests](https://github.com/andrewjpyle/programmatic_pages/actions/workflows/test.yml/badge.svg)](https://github.com/andrewjpyle/programmatic_pages/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 4.2+](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)

A Django reusable app for **programmatic SEO** at scale: take an entity table (zip codes, products, locations, people — anything you have a row for), pair each row with a content body, render to static HTML, and serve from your CDN. Schema.org JSON-LD, Open Graph, breadcrumbs, and a sane default template included.

Built for operators running content sites where the long tail is the product. Reference deploy: 11,000+ entity pages live, **2,236 pages/second** build rate.

> **Status: `0.1.0.dev0` — alpha.** API surface is settling. Production-tested via the reference deploy, but the public package itself is brand new — expect minor breaking changes before 1.0. Pin tightly.

---

## Why this exists

If you've ever:

- Generated a page-per-zip-code / page-per-product / page-per-location and watched your prerender service implode at 50K URLs
- Tried to ship "1 page per row in this Postgres table" and ended up writing an ad-hoc render script that drifted from your real templates
- Wanted clean Schema.org JSON-LD on every page without hand-rolling a serializer
- Looked for a Django reusable app that does this and found basically nothing

…then this is for you.

It does one thing well: **render a queryset of entity rows to static HTML at maximum throughput**, with the schema markup you'd want to write anyway.

---

## What it does

- ⚡ **Renders entity records to static HTML pages** from a Django template, in parallel.
- 🧱 **Pluggable adapter pattern** — works against the bundled `Page` model out of the box, or plug in your own model with one class.
- 🏷️ **Schema.org JSON-LD per page** with a per-page `schema_type` and free-form `schema_extras` for adding `Person`, `Place`, `Product`, etc. fields.
- 🍞 **N-level breadcrumb navigation** rendered into both HTML and `BreadcrumbList` JSON-LD.
- 🔄 **Build manifest** (`manifest.json`) emitted alongside output for downstream tooling.
- 📊 **Run audit log** (`PageBuild` model) — every build run tracked with status, count, errors, runtime.
- 🎛️ **Filtering** by `entity_type`, `status`, plus `--limit` and `--dry-run`.
- 🔌 **Bring your own template** with `--template myapp/custom.html`.

## What it deliberately doesn't do

- ❌ **Generate page bodies for you.** You bring the content (LLM, scraper, fixtures, your CMS — whatever). This tool ships it.
- ❌ **Deploy.** The output is a directory of `index.html` files. Pair it with nginx, Cloudflare Pages, S3+CloudFront, or your CI/CD of choice.
- ❌ **Track SEO performance.** Use Search Console, GA4, or similar. Build manifests integrate cleanly with whatever you already have.

---

## Quickstart (5 minutes)

### 1. Install

```bash
pip install programmatic_pages
```

### 2. Add to Django settings

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "programmatic_pages",
]

PROGRAMMATIC_PAGES = {
    "myproject": {
        "base_url": "https://example.com",
        "site_name": "Example",
        "ga_measurement_id": "G-XXXXXXXXXX",  # optional
    },
}
```

### 3. Migrate

```bash
manage.py migrate programmatic_pages
```

### 4. Add some pages

```python
from programmatic_pages.models import Page

Page.objects.create(
    project_key="myproject",
    entity_type="zip-codes",
    url_path="zip/10001/",
    title="ZIP 10001 — New York, NY",
    meta_description="Demographics, businesses, and city info for 10001.",
    h1="ZIP Code 10001",
    body_html="<p>Generated content goes here.</p>",
    schema_type="Place",
    status="published",
)
```

### 5. Build

```bash
manage.py build_static_pages --project myproject --output-dir ./build
```

```
Project: Example (myproject)
Base URL: https://example.com
Output: ./build
==================================================
  Built 1 pages (0 errors) in 0.0s
  Output: ./build
  Manifest: ./build/manifest.json
  Rate: 200 pages/s
  Build ID: 1
```

### 6. Serve

Point nginx (or Cloudflare Pages, or S3+CloudFront) at `./build`. You're done.

---

## The adapter pattern (when you have your own model)

The bundled `Page` model is a starting point. Most real users have their own page/entity model — maybe `Product`, `Listing`, `Article`. Don't migrate to ours. Write a 50-line adapter against yours.

```python
# myapp/adapters.py
from programmatic_pages.adapter import (
    BreadcrumbItem,
    PageAdapter,
    ProjectConfig,
    RenderablePage,
)

from myapp.models import Product, Site

class ProductPageAdapter(PageAdapter):
    def get_project_config(self, project_key: str) -> ProjectConfig:
        site = Site.objects.get(slug=project_key)
        return ProjectConfig(
            base_url=site.base_url,
            site_name=site.name,
            ga_measurement_id=site.ga_id,
        )

    def iter_pages(self, project_key, *, entity_type=None, status="published"):
        qs = Product.objects.filter(site__slug=project_key, status=status)
        if entity_type:
            qs = qs.filter(category__slug=entity_type)
        for product in qs.iterator():
            yield RenderablePage(
                url_path=f"products/{product.slug}/",
                title=f"{product.name} — {product.brand}",
                meta_description=product.short_description,
                h1=product.name,
                body_html=product.rendered_body,
                schema_type="Product",
                schema_extras={
                    "brand": {"@type": "Brand", "name": product.brand},
                    "offers": {
                        "@type": "Offer",
                        "price": str(product.price),
                        "priceCurrency": "USD",
                    },
                },
                breadcrumb_chain=[
                    BreadcrumbItem(label="Home", url="/"),
                    BreadcrumbItem(label="Products", url="/products/"),
                    BreadcrumbItem(label=product.category.name, url=f"/products/{product.category.slug}/"),
                    BreadcrumbItem(label=product.name),  # current page, no url
                ],
            )
```

Then run:

```bash
manage.py build_static_pages \
    --project myproject \
    --adapter myapp.adapters.ProductPageAdapter \
    --output-dir ./build
```

That's the whole integration story. The OSS package never knows about your model — it only sees `RenderablePage` dataclasses.

---

## Custom templates

Override the bundled template with `--template`:

```bash
manage.py build_static_pages --project myproject --template myapp/custom.html
```

Your template receives:

| Variable | Type | Notes |
|---|---|---|
| `title` | str | Page title |
| `meta_description` | str | |
| `canonical_url` | str | Absolute URL |
| `h1` | str | |
| `body_html` | str | Pre-rendered HTML; use `\|safe` |
| `schema_json` | str | JSON-LD payload; use `\|safe` |
| `breadcrumb_chain` | list[BreadcrumbItem] | Each has `.label` and `.url` |
| `base_url` | str | Project base URL |
| `site_name` | str | |
| `ga_id` | str | GA4 measurement ID, may be empty |
| `year` | int | Current year |
| `*` | * | Anything in `RenderablePage.extra_context` |

See [`src/programmatic_pages/templates/programmatic_pages/default.html`](src/programmatic_pages/templates/programmatic_pages/default.html) for the reference template.

---

## CLI reference

```bash
manage.py build_static_pages --project <key> [options]
```

| Flag | Default | Description |
|---|---|---|
| `--project` | required | Project key (key into `PROGRAMMATIC_PAGES` or your adapter's lookup) |
| `--adapter` | `programmatic_pages.adapters.DefaultPageAdapter` | Dotted path to a `PageAdapter` |
| `--template` | `programmatic_pages/default.html` | Template name or path |
| `--output-dir` | `~/programmatic_pages/build/<project>` | Where to write `index.html` files |
| `--entity-type` | (all) | Filter by `entity_type` |
| `--status` | `published` | Filter by status |
| `--limit` | `0` (all) | Cap pages built (useful for testing) |
| `--concurrency` | `4` | Parallel write threads |
| `--dry-run` | `false` | Count + show breakdown, write nothing |
| `--triggered-by` | `manual` | Logged on the `PageBuild` record (`manual`, `ci`, etc.) |

---

## Deployment

The output of a build is a tree of `index.html` files:

```
build/
├── manifest.json
├── zip/
│   ├── 00501/index.html
│   ├── 10001/index.html
│   └── ...
└── products/
    ├── widget-a/index.html
    └── ...
```

### nginx

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    root /var/www/example/build;

    # Trailing-slash URL paths map to index.html
    location / {
        try_files $uri $uri/index.html =404;
    }
}
```

### Cloudflare Pages / Vercel / Netlify

Treat the output directory as a static site. Most platforms map `foo/index.html` → `/foo/` automatically.

### CI integration

Run `build_static_pages` as a step in your CI/CD pipeline, then rsync/upload the output:

```yaml
- name: Build static pages
  run: |
    manage.py build_static_pages --project ${{ env.PROJECT_KEY }} \
        --output-dir ./build --triggered-by ci

- name: Deploy
  run: rsync -avz --delete ./build/ deploy@host:/var/www/myproject/
```

---

## Roadmap

`0.1.0` (next):
- [ ] `us_zip_codes` reference demo (~42K pages, demonstrates real throughput)
- [ ] `docs/` site with the adapter pattern guide and deployment cookbook

`0.2.0` (planned):
- [ ] Sitemap.xml generator (one-shot or chunked)
- [ ] Incremental builds (skip pages whose `updated_at` < last build)
- [ ] Cloudflare cache-purge hook on deploy

`Later`:
- [ ] Framework-agnostic core (Flask / FastAPI bindings)
- [ ] Optional Markdown-source-of-truth mode

---

## Contributing

Issues and PRs welcome. Run the test suite locally with:

```bash
git clone https://github.com/andrewjpyle/programmatic_pages.git
cd programmatic_pages
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q
```

---

## License

MIT. See [LICENSE](LICENSE).

---

## Author

Built and maintained by [Andrew J. Pyle](https://andrewjpyle.com). Originally extracted from production infrastructure running a portfolio of programmatic SEO sites.
