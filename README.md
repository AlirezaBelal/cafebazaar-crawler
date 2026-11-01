# CafeBazaar Crawler

**A small, local-first tool for exploring public CafeBazaar Android app metadata.**

Collect permitted public app information to SQLite, browse it in a searchable **offline HTML report**, or export a safe CSV. No account, cloud service, API key, dashboard server, or telemetry is required.

> This is an independent research tool, **not an official CafeBazaar product**. Upstream API availability and permission to collect data may vary. The offline product works without CafeBazaar access; successful live extraction is not guaranteed.

## Start in 30 seconds — no network

Requirements: **Python 3.9 or newer**. The offline demo uses only the Python standard library.

**Windows:** Double-click `scripts/desktop-demo.cmd`. It generates twelve clearly labelled **synthetic** apps and opens a local HTML report.

Or use a terminal (Windows, macOS, Linux):

```bash
python src/main.py --demo
```

Open `data/demo-report.html` in your browser. **No real apps are fetched.** If the demo already exists, use `--db data/another-demo.db`; the tool will not overwrite an existing database with synthetic records.

The report uses a new Persian-first premium RTL dashboard with responsive cards, charts, a searchable and sortable app table, a category filter, accessible empty states, and an optional dark theme. All assets are embedded in the generated HTML; it needs no server, CDN, or internet access. It is a standalone HTML file with no external dependencies. It intentionally omits contact details.

## Collect real public metadata (optional)

Only do this if you are allowed to access the underlying public endpoints. Respect CafeBazaar's terms, robots/access policies, and reasonable request rates.

First create a virtual environment and install the network dependencies:

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run a **small bounded crawl** (rather than an unbounded one):

```bash
python src/main.py --category-limit 1 --subcategory-limit 1 --max-apps 5 --max-list-pages 1 --max-subcategory-pages 1
```

The database is saved to `data/cafebazaar_results.db` by default. `--max-apps` caps successfully saved app details, while `--max-list-pages` and `--max-subcategory-pages` separately limit how many API listing pages are requested **per path**. Those flags are not a global request cap, and retries may make additional requests. To reduce pressure, keep conservative delays.

A plain `python src/main.py` intentionally **does not send requests**. To opt into an unbounded collection after reviewing source permissions, use `python src/main.py --full`. Do not use this as a first run.

## Browse or export saved data

```bash
# Produce a responsive offline browser report (up to 500 rows by default)
python src/main.py --report data/report.html

# Export all selected metadata (UTF-8 with spreadsheet formula protection)
python src/main.py --export-csv data/apps.csv

# Use a custom SQLite database
python src/main.py --db data/my-run.db --report data/my-report.html
```

The HTML report displays up to 1,000 records, configurable with `--report-limit`; CSV exports the selected fields for all available rows. For larger collections, use CSV and further analysis tools. Generated reports and local databases are not committed to Git.

The SQLite table `app_details` uses `(package_name, source)` as its primary key and is compatible in structure with the companion [Myket Crawler](https://github.com/AlirezaBelal/myket-crawler).

## Verify a real collection from your own computer

A small **opt-in** end-to-end live smoke checks one category page, one subcategory page, one app list page, one app detail response and a write to a **temporary database**:

```bash
python tests/live_smoke.py --yes-live
```

This test needs installed dependencies and Internet access. It runs only when explicitly requested; it is **not executed automatically by CI** and does not retain a dataset. It may fail due to DNS, geographic access restrictions, API changes, upstream errors, or site policy. If it fails, do not bypass access restrictions.

## Quality and safety

- Offline, deterministic `unittest` tests run through GitHub Actions.
- Inputs and package IDs are validated where possible; duplicate packages are skipped within a crawl.
- Requests have timeouts and retries; pagination stops on repeated pages and supports explicit page budgets.
- SQLite updates reuse the same package/source key, rather than accumulating duplicate rows.
- Report values are HTML-escaped; developer email and phone fields are not included in the report.
- CSV protects spreadsheet cells that resemble formulas.
- Local demo never calls the network; generated demo records are fictional.
- Ctrl+C stops real crawling and preserves already saved database rows.
- Secrets, SQLite databases, generated HTML/CSV, environments, and logs should never be committed.

Check `python src/main.py --help` for complete options. All numeric limits are nonnegative; `0` means unlimited. Network delays are configured via `CAFEBAZAAR_CATEGORY_DELAY_MS` (default 10000), `CAFEBAZAAR_SUBCATEGORY_DELAY_MS` (default 2000), and `CAFEBAZAAR_APP_DELAY_MS` (default 100). Set custom output with `--db` or the environment variables `CAFEBAZAAR_DATA_DIR` and `CAFEBAZAAR_DB_PATH`.

## Project layout

```text
src/main.py                 Command-line interface and safe entry point
src/bazarService.py         CafeBazaar network adapter
src/models/AppDetails.py    Shared SQLite record model
src/local_report.py         Offline demo, HTML report and CSV export
scripts/desktop-demo.cmd    Windows demo launcher
tests/                     Offline tests and opt-in live_smoke.py
data/                      Ignored local datasets and reports
```

## Project status and licensing

Offline demo, reporting, CSV and deterministic tests are ready to use once verified by CI. Live extraction is **best effort** and depends on the current upstream API; do not claim production coverage or completeness without a successful authorized live smoke test.

MIT license — see [LICENSE](LICENSE).

**Privacy:** Research may collect public developer contacts into your *local* SQLite file. Treat it as personal data if applicable. The offline HTML report and CSV intentionally exclude contact fields. Review and remove sensitive data before publishing or sharing any dataset.
