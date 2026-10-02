"""Render one page from a hostile record with the default template and show what a browser sees.

    python examples/hostile_record.py

The record's name tries to close the JSON-LD <script> and open its own, and its description
carries quotes and an ampersand. No database needed.
"""

import json
from html.parser import HTMLParser

import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=["programmatic_pages"],
    TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}],
)
django.setup()

from django.template.loader import get_template  # noqa: E402

from programmatic_pages import ProjectConfig, RenderablePage  # noqa: E402
from programmatic_pages.builder import render_page  # noqa: E402

NAME = 'Evil Park</script><script>alert("pwned")</script>'
page = RenderablePage(
    url_path="parks/evil/",
    title=NAME,
    meta_description='Has a "quoted" pond & a dock.',
    h1=NAME,
    body_html="<p>body</p>",
    schema_type="Park",
)
project = ProjectConfig(base_url="https://parks.example.com", site_name="Example County Parks")
html = render_page(page, project, get_template("programmatic_pages/default.html").template)


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found, self._cur = [], None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._cur = [dict(attrs).get("type") or "(classic script)", ""]
            self.found.append(self._cur)

    def handle_endtag(self, tag):
        if tag == "script":
            self._cur = None

    def handle_data(self, data):
        if self._cur is not None:
            self._cur[1] += data


for line in html.splitlines():
    if 'name="description"' in line or "ld+json" in line:
        print(line.strip())

parser = Scripts()
parser.feed(html)
print(f"script elements a browser would see: {len(parser.found)}")
for kind, body in parser.found:
    try:
        name = json.loads(body)[0]["name"]
        print(f"  {kind}: valid JSON, name == record name: {name == NAME}")
    except (ValueError, KeyError, IndexError):
        print(f"  {kind}: NOT valid JSON-LD, body starts {body.strip()[:40]!r}")
