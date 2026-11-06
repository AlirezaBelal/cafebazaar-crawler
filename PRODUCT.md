# CafeBazaar Crawler — supported product scope

CafeBazaar Crawler is local Python software: **CLI → permitted HTTP/API responses → parsing and validation → SQLite → optional HTML/CSV.** It uses `requests` and `src/bazarService.py`, not Selenium. Its static product website and portfolio provide installation information; neither runs a collector or accepts datasets.

## Implemented behavior

- Explicit opt-in live collection; no-argument startup and offline demo/report/export modes make no marketplace requests.
- Category/subcategory discovery, listing pagination, package deduplication, and SQLite replacement by package/source.
- Successful-app limits and separate per-path page limits. Numeric CLI limits are nonnegative; `0` is unlimited. `--full` has no default global budget.
- Thirty-second HTTP timeouts, retries on selected server failures, and separate detail retries. Sessions close in `finally`.
- Repeated-page stopping and a three-consecutive-error subcategory threshold.
- Response package matching before persistence, Persian reports, formula-safe CSV, atomic exports, and SQLite recovery-file protection.

## Request and failure boundaries

The app limit counts saved details, not HTTP calls. Subcategory pages are limited per category and listing pages per subcategory. Discovery can retrieve a page containing more apps than the save limit. There is no global request, runtime, or byte budget.

Transport retries allow five retries for 500/502/503/504 responses with backoff. Detail requests have up to three application attempts; these layers can multiply requests. Detail responses 401/403/429 stop that detail without another application retry. Operators must stop when access is refused; this is not an automated policy-compliance system. Configured category/subcategory/detail delays supplement pagination and retry delays.

Some adapter paths return an empty list for both empty data and upstream errors. Discovery failure state is not always structured. Nested null/type handling is best-effort, and optional fields can be absent. Empty output is not evidence that no apps exist. The release does not establish current endpoint availability, real pagination offsets, or live response compatibility.

## Exit codes

| Exit | Meaning |
| --- | --- |
| 0 | Offline operation succeeded, or a live run saved at least one app without recorded detail failures |
| 1 | Empty or partially failed live collection, including reaching an app limit after a recorded failure |
| 2 | Invalid arguments, missing/incompatible database, or handled local I/O error |
| 130 | Interruption inside the crawl loop; saved rows remain intact |

These local outcomes cannot prove complete coverage or detect every upstream omission.

## Data handling

Raw SQLite can contain optional developer contacts. HTML/CSV omit phone and email and must still be reviewed before sharing. Formula-like CSV text is escaped. Exports use temporary files and atomic replacement, with protection for the main database and WAL/SHM/journal paths and existing aliases. Concurrent filesystem alias changes are not fully race-proof. CSV currently loads selected rows into memory.

The website uses local CSS/SVG with no scripts, uploads, analytics, external font service, or marketplace connection. Useful generated reports retain their browser-local importer and other controls.

## Maintenance priorities

Maintain parsers against authorized reproducible fixtures and keep dependencies compatible. A global request budget, simpler retry policy, streaming CSV, structured discovery failures, and stricter optional-field validation are future work. Resumable crawling, scheduled services, live API guarantees, and hosted analysis are not shipped.

Run the offline checks in [README.md](README.md). Live smoke remains a separately authorized operation. No live CafeBazaar collection was performed for this release.
