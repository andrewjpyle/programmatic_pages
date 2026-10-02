"""Check a parks demo build the way a crawler would read it.

    python check_build.py ./build

For every eligible Park: exactly one page exists, its single ld+json block parses, and its
canonical URL and JSON-LD url both equal the address the file is served from. Parks that are not
eligible must have no page. Exits 1 on the first broken promise.
"""

import json
import os
import sys
from html.parser import HTMLParser
from pathlib import Path


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ld: list[str] = []
        self.scripts = 0
        self.canonical = None
        self._buf = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            self.scripts += 1
            self._buf = [] if a.get("type") == "application/ld+json" else None
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")

    def handle_endtag(self, tag):
        if tag == "script" and self._buf is not None:
            self.ld.append("".join(self._buf))
            self._buf = None

    def handle_data(self, data):
        if self._buf is not None:
            self._buf.append(data)


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "build").resolve()
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import django

    django.setup()
    from django.conf import settings
    from parks.adapters import _eligible
    from parks.models import Park

    base = settings.PARKS_SITE["base_url"].rstrip("/")
    eligible = set(_eligible().values_list("slug", flat=True))
    pages = sorted(out.rglob("index.html"))
    problems = []

    for slug in sorted(Park.objects.values_list("slug", flat=True)):
        f = out / "parks" / slug / "index.html"
        if slug not in eligible:
            if f.exists():
                problems.append(f"{slug}: not eligible but has a page")
            else:
                print(f"skip  /parks/{slug}/  (no page: not enough data)")
            continue
        if not f.exists():
            problems.append(f"{slug}: eligible but no page")
            continue
        head = Head()
        head.feed(f.read_text(encoding="utf-8"))
        expected = f"{base}/parks/{slug}/"
        try:
            primary = json.loads(head.ld[0])[0] if len(head.ld) == 1 else None
        except json.JSONDecodeError as e:
            primary = None
            problems.append(f"{slug}: JSON-LD does not parse ({e})")
        if head.scripts != 1 or primary is None:
            problems.append(f"{slug}: expected exactly one parseable ld+json script")
        elif head.canonical != expected or primary.get("url") != expected:
            problems.append(f"{slug}: canonical/url mismatch")
        else:
            print(f"ok    /parks/{slug}/  canonical == JSON-LD url, {primary['@type']}, 1 script")

    if len(pages) != len(eligible):
        problems.append(f"{len(pages)} pages on disk for {len(eligible)} eligible parks")

    for p in problems:
        print(f"FAIL  {p}")
    print(f"{len(pages)} pages for {Park.objects.count()} parks, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
