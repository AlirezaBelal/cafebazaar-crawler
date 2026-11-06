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

## Local-software product release — 2026-11-06

The historical audit above is preserved. This review starts from master `4f5049635539c40612bc954887f5f00e3ae3d6e4` and does not establish live CafeBazaar compatibility.

Confirmed defects and corrections:

- Partial failures could return success, including at the app limit; empty runs could also return success. Deterministic CLI regressions now require nonzero status in these cases.
- Exports did not protect WAL/SHM/journal destinations or preserve an existing output after a write failure. Added recovery-name/alias guards and atomic temporary-file publication.
- App-detail responses were not compared with the requested package before persistence. Added request identifier validation and response identity matching.
- Detail retries continued on access refusal. Stop application retries for 401/403/429; transport Retry-After handling is disabled so 429 is not retried by that layer.
- Pages published a fictional dashboard and README described hosted import as a product feature. Publish the static `site/` product guide; preserve locally generated reports and their importer.

The pinned design and web-ui-audit revisions remain unchanged. The brand register guided a forest/mint centered composition and custom response-flow SVG, with native sans typography (32–56px hero, 24–36px section headings), focusable code blocks, reduced motion, local assets, and a no-script/no-connect CSP. Automated Chromium screenshots and WCAG scans cover the new website and public portfolio route at all seven required widths. Merge-time Actions artifacts and job results are the verification record; no live marketplace request is used by the release tests.

Known boundaries remain: page limits are per path, retries are layered, there is no global network budget, empty discovery can represent failure, optional nested-field types are not completely normalized, and current API access/shape compatibility is unverified. Raw SQLite can contain developer contacts; reports and CSV omit phone/email. Future source/API work requires authorized fixtures and separate scope.

Visual review found and corrected fixed-height scaling of the architecture SVG on mobile; Chromium now checks its intrinsic aspect ratio. The existing local-report QA now waits on locator text instead of string evaluation, preserving the report CSP. Browser tooling is pinned to supported runner/package versions. Production portfolio QA covers the deferred analytics-loading window; the CafeBazaar route opts out through a default-off shared-layout prop without changing analytics defaults on other routes.
