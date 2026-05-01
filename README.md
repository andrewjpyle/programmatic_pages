# programmatic_pages

> Generate millions of SEO-quality static pages from a Django queryset, at thousands per second.

A Django reusable app for **programmatic SEO** at scale: take an entity table (zip codes, products, locations, people, anything), pair each row with a content body, render to static HTML, and serve from your CDN. Schema.org JSON-LD, Open Graph, breadcrumbs, and a sane default template are all included.

Built for operators running content sites where the long tail is the product. Reference deploy: 11,000+ entity pages live, 2,236 pages/second build rate.

## Status

`0.1.0.dev0` — alpha, API surface is settling. Not yet on PyPI.

## Quickstart

```bash
pip install programmatic_pages
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "programmatic_pages",
]
```

```bash
manage.py migrate programmatic_pages
manage.py build_static_pages --project myproject --output-dir ./build
```

Full quickstart, the adapter pattern, and the deployment guide are in `docs/` (coming as v0.1.0 lands).

## What it does

- **Renders** entity records into static HTML pages from a Django template.
- **Parallelizes** the render+write loop (configurable concurrency).
- **Generates Schema.org JSON-LD** per page with a pluggable type map.
- **Builds breadcrumb navigation** of arbitrary depth.
- **Tracks every build** in a `PageBuild` model so you can audit runs.
- **Writes a manifest.json** alongside the output for downstream tooling.

## What it doesn't do

- **It doesn't generate page bodies for you.** You bring the content; this tool ships it.
- **It doesn't deploy.** The output is a directory of `index.html` files. Pair it with nginx, Cloudflare Pages, S3+CloudFront, or your CI/CD of choice.
- **It doesn't track SEO performance.** Use Search Console, GA4, or similar.

## License

MIT. See [LICENSE](LICENSE).
