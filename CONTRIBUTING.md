# Contributing

Thanks for the interest. `programmatic_pages` is an early-stage project; PRs and issues are welcome but expect a real review before anything lands.

## Before you open a PR

- **Open an issue first** for non-trivial changes (anything beyond a typo, doc fix, or small bug). Discussion saves both of us time.
- **One concern per PR.** Prefer multiple small PRs over one giant one.
- **Match the existing style.** Ruff is the source of truth.

## Local setup

```bash
git clone https://github.com/andrewjpyle/programmatic_pages.git
cd programmatic_pages

# Recommended: uv (https://github.com/astral-sh/uv)
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or with stdlib venv + pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running the suite

```bash
ruff check .             # lint
pytest -q                # 17 tests, runs in <1 second
```

CI runs on push and PR against `main`. The matrix tests Python 3.10/3.11/3.12 × Django 4.2/5.0/5.1. If your change needs a wider matrix (older Python, older Django), say so in the PR.

## Trying the demo

```bash
cd examples/us_zip_codes
python manage.py migrate
python seed.py
python manage.py build_static_pages --project us_zip_codes --output-dir ./build
```

Open `build/zip/10001/index.html` to verify your change didn't regress output.

## What kinds of changes land easily

- Bug fixes with a regression test.
- Small DX improvements with no API change (better error messages, clearer help text, faster path).
- Documentation tightening.
- New optional features with `--flag` opt-in (no behavior change for existing users).

## What kinds of changes need discussion first

- API surface changes to `PageAdapter`, `RenderablePage`, `ProjectConfig`, `BreadcrumbItem`, or the management command's flags.
- Anything that touches the build manifest schema.
- Adding non-Django frameworks (this is on the roadmap but warrants a design discussion).
- New runtime dependencies.

## Commit messages

Conventional Commits style preferred but not enforced:

- `feat: ...` / `fix: ...` / `docs: ...` / `test: ...` / `refactor: ...` / `chore: ...`
- One-line summary, then a blank line, then the body if needed.

## Code of conduct

Be excellent to each other. Substantive disagreement is welcome; personal attacks aren't.

## License

By contributing, you agree your work ships under the [MIT license](LICENSE).
