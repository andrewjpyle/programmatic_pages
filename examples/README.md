# Examples

Runnable demos for `programmatic_pages`. Both use SQLite and need nothing but `pip install -e .`
from the repo root.

| Demo | Shows | Data |
|---|---|---|
| [`parks_demo/`](parks_demo/) | Your own model plus a custom adapter, a per-record eligibility rule, and a checker that parses every page's JSON-LD and canonical | 7 fictional parks (SAMPLE DATA) |
| [`us_zip_codes/`](us_zip_codes/) | The bundled `Page` model with no adapter code | 50 real ZIP codes (public reference data) |

## Adding your own

A demo should run in a few commands, use public-domain or clearly fictional data, and show one
feature well. Open an issue or a PR.
