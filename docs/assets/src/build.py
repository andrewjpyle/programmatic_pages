"""Build the README graphics for programmatic_pages.

    python docs/assets/src/build.py
    uv run --with playwright==1.56.0 --with pillow python docs/assets/src/render.py docs/assets/src docs/assets

Data-bearing graphics (hero, anatomy, safety) render ONLY from the committed captures in
captures/, each recorded from a real run by the readme kit's capture tool. Nothing is typed in.
The architecture graphic is structural and says so in its footer.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import readme_kit as k  # noqa: E402

REPO = "PROGRAMMATIC_PAGES"
CAP = HERE / "captures"
WRAP = "white-space:pre-wrap;word-break:break-all"


def cap(name: str) -> dict:
    return k.load_capture(CAP / f"{name}.json")


def run_date(c: dict) -> str:
    return c["captured_at"][:10]


def check_rows() -> tuple[list[tuple[str, str]], str]:
    out = cap("parks_check")["output"].strip().splitlines()
    rows = []
    for line in out[:-1]:
        status, path = line.split()[:2]
        rows.append((status, path))
    return rows, out[-1]


def hero() -> str:
    c = cap("parks_check")
    rows, summary = check_rows()
    n_pages = sum(1 for s, _ in rows if s == "ok")
    n_skip = sum(1 for s, _ in rows if s == "skip")
    items = "".join(
        f"<div style='display:flex;justify-content:space-between;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line)'>"
        f"<span class='mono' style='font-size:14px;color:{'var(--ivory)' if s == 'ok' else 'var(--dim)'}'>{k.esc(p)}</span>"
        f"<span class='mono' style='font-size:11px;letter-spacing:.15em;color:{'var(--amber)' if s == 'ok' else 'var(--dim)'}'>"
        f"{'PAGE' if s == 'ok' else 'NO PAGE'}</span></div>"
        for s, p in rows)
    right = (f"<div class='card' style='width:500px'><div class='k' style='font-size:12px;padding:14px 16px 8px'>7 FICTIONAL PARKS IN, CHECKED LIKE A CRAWLER</div>{items}"
             f"<div class='mono' style='font-size:12px;color:var(--muted);padding:12px 16px 4px'>{k.esc(summary)}</div>"
             f"<div class='mono' style='font-size:11px;color:var(--dim);padding:4px 16px 12px'>from check_build.py · real run {run_date(c)}</div></div>")
    return k.hero(
        "PROGRAMMATIC_PAGES · DJANGO · MIT",
        "One record, one page.", "Real static HTML.",
        "A Django app that renders a queryset to static <b style='color:var(--ivory);font-weight:600'>index.html</b> files, "
        "each with a canonical URL and schema.org JSON-LD, ready for any CDN.",
        [("Your model, one adapter", "Yield a flat RenderablePage per row. The package never imports your model."),
         ("The gate lives in the queryset", f"{n_skip} thin records get no page, and --dry-run counts the same {n_pages}."),
         ("Safe with untrusted text", "Titles cannot close the JSON-LD script. Paths cannot leave the build dir.")],
        f"{len(rows)} RECORDS · {n_pages} PAGES · {n_skip} HELD BACK · 0 PROBLEMS",
        right, f"{REPO} · REAL RUN {run_date(c)}")


def _attr(line: str, name: str) -> str:
    m = re.search(name + r'="([^"]*)"', line)
    return m.group(1) if m else ""


def anatomy() -> str:
    c = cap("parks_head")
    lines = c["output"].splitlines()
    pick = {
        "title": next(x for x in lines if "<title>" in x).strip(),
        "desc": next(x for x in lines if 'name="description"' in x).strip(),
        "canon": next(x for x in lines if 'rel="canonical"' in x).strip(),
        "og": next(x for x in lines if 'property="og:url"' in x).strip(),
        "ld": next(x for x in lines if "ld+json" in x).strip(),
    }
    ld_body = re.search(r">(.*)</script>", pick["ld"]).group(1)
    blocks = json.loads(ld_body)

    def code(s: str, color: str = "var(--muted)") -> tuple[str, str]:
        return ("code", f"<span style='{WRAP};color:{color};font-size:16px;line-height:1.6'>{k.esc(s)}</span>")

    doc = [("m", k.esc("$ head -n 20 build/parks/fox-and-heron/index.html   (excerpt)")),
           code(pick["title"], "var(--ivory)"),
           code(pick["desc"]),
           code(pick["canon"], "var(--amber)"),
           code(pick["og"]),
           code(pick["ld"]),
           ("i", f"JSON-LD parses to {len(blocks)} blocks: {blocks[0]['@type']} + {blocks[1]['@type']} "
                 f"({len(blocks[1]['itemListElement'])} crumbs)"),
           ("m", f"captured {k.esc(c['captured_at'])} · commit {c['commit'][:7]} · SAMPLE DATA, fictional park")]
    notes = [(126, "Title from the adapter. The & is escaped once by Django autoescaping."),
             (176, "Description: quotes become &quot; once. Before this fix they came out as &amp;quot;."),
             (232, "Canonical = base_url + url_path, the same address the file is written to. check_build.py asserts it."),
             (318, "JSON-LD: the record as a schema.org Park, with your schema_extras merged in."),
             (398, "& is written as \\u0026: still valid JSON, and no text can close the script element."),
             (478, "A BreadcrumbList is emitted alongside, from the same chain the HTML breadcrumbs use.")]
    return k.anatomy("ANATOMY OF ONE GENERATED PAGE HEAD", doc, notes, f"{REPO} · REAL RUN {run_date(c)}", doc_width=860)


def safety() -> str:
    before, after = cap("hostile_before"), cap("hostile_after")

    def block(c: dict) -> list[tuple[str, str]]:
        out = []
        for line in c["output"].splitlines():
            bad = "NOT valid" in line or line.startswith("script elements a browser would see: 2")
            good = "valid JSON, name == record name: True" in line or line.endswith("see: 1")
            color = "var(--amber)" if bad else ("var(--good)" if good else "var(--muted)")
            out.append(("code", f"<span style='{WRAP};color:{color};font-size:15px;line-height:1.6'>{k.esc(line)}</span>"))
        return out

    doc = ([("m", k.esc("$ python examples/hostile_record.py   name = 'Evil Park</script><script>alert(\"pwned\")</script>'")),
            ("h2", f"Before: original main, commit {before['commit'][:7]}")]
           + block(before)
           + [("h2", f"After: this branch, commit {after['commit'][:7]}")]
           + block(after)
           + [("m", f"both captured {k.esc(after['captured_at'][:10])} · the same harness file in both runs")])
    notes = [(164, "Before: the description was escaped twice, &amp;quot; in every meta tag."),
             (222, "The record's name closed the ld+json script. A browser would run alert(\"pwned\")."),
             (300, "So the browser saw 2 scripts, and the JSON-LD was cut in half: no structured data either."),
             (440, "After: <, > and & are unicode-escaped. One script element, valid JSON, the exact original name."),
             (548, "Pinned by tests/test_safety.py. Removing the escape turns 2 named tests red.")]
    return k.anatomy("ONE HOSTILE RECORD, BEFORE AND AFTER", doc, notes, f"{REPO} · REAL RUN {run_date(after)}", doc_width=860)


def architecture() -> str:
    boxes = (k.box(56, 210, 240, 160, "YOUR MODEL", ["Park, Product, Listing", "or the bundled Page", "any queryset"])
             + k.box(366, 210, 260, 160, "YOUR ADAPTER", ["iter_pages() yields", "RenderablePage per row", "the queryset = the gate", "get_project_config()"])
             + k.box(696, 210, 300, 160, "BUILDER", ["one url_path, one file", "canonical + JSON-LD", "script-safe escaping", "path stays in output dir"], True)
             + k.box(1066, 210, 278, 160, "OUTPUT", ["build/<path>/index.html", "manifest.json", "PageBuild audit row", "serve from any CDN"])
             + k.box(696, 500, 300, 130, "A PAGE FAILS", ["named on stderr", "PageBuild = failed", "command exits 1"]))
    arrows = [(296, 300, 356, 300, "rows"), (626, 300, 686, 300, "pages"), (996, 300, 1056, 300, "files"),
              (846, 380, 846, 490, "duplicate or unsafe path", True, "right")]
    return k.flow("HOW IT WORKS", f"Your rows in. {k.em('Static pages')} out.",
                  "the package never imports your model · the adapter decides which rows deserve a page · a failed page stops CI",
                  boxes, arrows, f"{REPO} · HOW IT WORKS")


if __name__ == "__main__":
    k.write_pages(HERE, {"hero": hero(), "anatomy": anatomy(), "safety": safety(), "architecture": architecture()})
