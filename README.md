# CafeBazaar Crawler

**Local Python software for collecting permitted public CafeBazaar app metadata into SQLite.**

[Product website](https://alirezabelal.github.io/cafebazaar-crawler/) · [Portfolio](https://alirezabelal.github.io/work/lab/cafebazaar-crawler/) · [راهنمای فارسی](QUICKSTART.fa.md) · [Product scope](PRODUCT.md)

[![Offline tests](https://github.com/AlirezaBelal/cafebazaar-crawler/actions/workflows/tests.yml/badge.svg)](https://github.com/AlirezaBelal/cafebazaar-crawler/actions/workflows/tests.yml)

The collector runs on your computer. Python HTTP requests retrieve supported responses, the adapter parses app metadata, and SQLite stores local records. Optional Persian RTL HTML reports and CSV exports support offline review. The static product website documents installation; it does not run a collector or accept datasets.

This independent project is not an official CafeBazaar service. Current live API availability and compatibility have not been verified for this release. Public endpoint availability does not establish collection permission.

## Installation

Requires **Python 3.9+**. No browser or Selenium is needed. The offline demo uses only the Python standard library.

```bash
git clone https://github.com/AlirezaBelal/cafebazaar-crawler.git
cd cafebazaar-crawler
```

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe src\main.py --demo
```

**macOS / Linux**

```bash
python3 -m venv .venv
. .venv/bin/activate
python src/main.py --demo
```

Open `data/demo-report.html`. This creates twelve fictional records in `data/demo.db` with no network requests. It preserves existing demo databases: use `--db data/demo-2.db` for another run. Windows also provides `scripts/desktop-demo.cmd`.

## Small, permitted collection

Confirm applicable terms and technical access rules first. Never bypass authentication, CAPTCHA, rate limits, or anti-bot controls. Stop when access is refused.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py --category-limit 1 --subcategory-limit 1 --max-apps 3 --max-list-pages 1 --max-subcategory-pages 1
```

```bash
# macOS / Linux, with the environment activated
python -m pip install -r requirements.txt
python src/main.py --category-limit 1 --subcategory-limit 1 --max-apps 3 --max-list-pages 1 --max-subcategory-pages 1
```

The default database is `data/cafebazaar_results.db`; choose another with `--db`. Running without arguments makes no requests. `--full` deliberately opts into unbounded collection and should not be a first run.

**These are not global request limits.** `--max-apps` counts successful saves. Listing pages are limited per subcategory; subcategory pages per category. `0` means unlimited. Discovery precedes app saving, and layered retries can issue additional requests. Keep conservative delays: defaults are 10 seconds per category, 2 seconds per subcategory, and 100 milliseconds per detail loop, with extra pagination/retry delays. Environment settings are `CAFEBAZAAR_CATEGORY_DELAY_MS`, `CAFEBAZAAR_SUBCATEGORY_DELAY_MS`, and `CAFEBAZAAR_APP_DELAY_MS`.

## Local output

Using the virtual environment's Python executable:

```bash
python src/main.py --db data/my-run.db --report data/my-report.html
python src/main.py --db data/my-run.db --export-csv data/my-apps.csv
```

Reports provide Persian RTL search, filters, sorting, themes, and a local CSV/JSON importer. That importer remains in locally generated reports only. Reports show 500 rows by default (`--report-limit 1..1000`); CSV includes all selected rows and currently loads them into memory.

HTML and CSV omit developer phone and email fields. CSV neutralizes formula-like cells. Exports publish atomically and cannot replace the source database or its WAL/SHM/journal files. Raw SQLite may contain developer contacts: keep databases and logs private and review obligations before sharing. SQLite uses the `app_details` table with `(package_name, source)` identity; repeat records replace the existing row.

## Tests

```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
node --test tests/test_report_import.cjs tests/test_product_site.mjs
```

CI uses synthetic fixtures and temporary databases on Python 3.9/3.14 Ubuntu and Python 3.12 Windows. Chromium checks the new product website and portfolio at seven widths; screenshots and WCAG reports are Actions artifacts. Browser tooling is CI-only.

`python tests/live_smoke.py --yes-live` is a separate opt-in live test. Do not run it without confirming authorization. It was not run for this release; offline success does not prove current API compatibility.

## Documentation and troubleshooting

- [Architecture, supported scope, exit codes, and limitations](PRODUCT.md)
- [Persian quickstart](QUICKSTART.fa.md)
- [Preserved audit history and release findings](AUDIT.md)
- Existing demo: choose a fresh `--db` path.
- Python unavailable on Windows: install Python 3.9+ and confirm `py -3 --version`.
- Locked database: close competing writers, retain a backup, and retry.
- API errors: stop and review access restrictions or changed response shapes; do not bypass them.

```text
src/       Local CLI, HTTP adapter, SQLite model, offline outputs
site/      Static product website and original SVG assets
tests/     Deterministic regressions and browser QA
scripts/   Windows demo launcher
data/      Ignored local databases and outputs
```

Licensed under [MIT](LICENSE). No telemetry, public proxy, hosted database, or runtime web framework is included.
