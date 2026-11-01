# Product audit — 2026-11-01

Scope: current master at `014a88c`, all 30 reachable commits, merged PRs #1–#4, Python modules, SQLite model, CLI, offline report, launcher, tests and workflows. Public visibility and the master default branch were confirmed. No open issues or PRs existed at the start; only master remained remotely.

## Verified corrections

- Reject report/CSV paths that alias the input database, including hard links and symlinks, and reject database extensions for exports. Previously either exporter could truncate its SQLite source.
- Substitute HTML template markers once. Previously marker-like category text could expand into later report fragments and damage markup.
- Reject app-detail payloads without a usable package identity before creating a database.
- Reset the subcategory error counter only after successful parsing. Previously repeated malformed responses could retry forever.
- Close each request session in a finally block, including request exceptions.
- Keep the fictional-demo badge visible on small screens and replace the misleading “real data” statement with the actual report mode.
- Expand browser acceptance from four to all seven requested widths, add rating sorting, keyboard search, theme round-trip and JavaScript-error checks; also run visual CI on relevant master pushes.
- Ignore screenshot artifacts and document troubleshooting and installed-browser QA.

## Local verification

- Python 3.14 on Windows: compilation passed; 25 unittest cases passed (20 before changes).
- Installed Chrome through Playwright: 320, 375, 390, 768, 1024, 1440 and 1920 px passed, no document overflow, external HTTP requests or JavaScript errors. Search, empty-state reset, category filter, install/rating sorting, keyboard shortcut and both themes passed. Responsive screenshots were inspected before the UI correction.
- Historical credential-pattern scan: 30 commits, no matches for common GitHub/OpenAI/AWS key patterns or private-key headers. Historical file inventory contained no committed databases or datasets. This is a bounded heuristic review, not proof that every possible secret is absent.
- Existing tests cover SQLite upsert/cleanup, escaping, contact omission, UTF-8/formula-safe CSV, empty reports, CLI validation, page budgets and duplicate-page stopping. Added tests cover the verified defects above.

## Boundaries and remaining risks

- No live crawl was run. Current CafeBazaar terms restrict bot access; explicit source permission must be established first: https://cafebazaar.ir/terms . API availability, current response shapes and live pagination offsets remain unverified.
- Full WCAG 2.2 AA certification was not performed. Keyboard checks are limited; tiny helper text, color contrast, mobile table semantics and screen-reader behavior still need a dedicated accessibility review.
- SQLite dynamic typing can admit invalid numeric data from externally edited databases; reports expect numeric install/rating values. Upstream nested null/type handling is incomplete, though malformed subcategory retries now terminate.
- Network retries are layered and listing budgets are per path, not a global request or time budget. An empty listing can still represent either no data or an upstream failure.
- CSV currently loads all selected rows into memory. Large datasets may need streaming export.
- The Windows launcher source was reviewed, but double-click launching was not exercised. Python is still required; packaging was not added because signing and per-platform builds would substantially increase maintenance.
- No dependencies, schema migration, remote assets or dashboard framework were introduced. No credential rotation or history rewriting was performed.

CI and merge status must be checked on the PR and final master commit; local results alone do not establish cross-platform success.
