# cafebazaar-crawler

A lightweight Python crawler that collects public app metadata from CafeBazaar and stores the results in a local SQLite database.

## What it does

- Fetches CafeBazaar categories and subcategories
- Paginates through app lists
- Fetches detailed metadata for each app
- Stores results in SQLite with one row per `package_name + source`
- Captures app name, package, developer info, install count, ratings, category, tags, descriptions, price, version, and update time
- Retries transient HTTP failures and stops cleanly after repeated failures
- Skips duplicate packages during a single run
- Prints a crawl summary on completion or `Ctrl+C`

## Requirements

- Python 3.9+
- `requests`
- `jdatetime`
- SQLite (included with Python)

## Quick start

```bash
git clone https://github.com/AlirezaBelal/cafebazaar-crawler.git
cd cafebazaar-crawler
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py --max-apps 20
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py --max-apps 20
```

`--max-apps 20` is a convenient smoke test. Remove the option for a full crawl.

## Usage

Full crawl:

```bash
python src/main.py
```

Small controlled run:

```bash
python src/main.py --category-limit 1 --subcategory-limit 1 --max-apps 20
```

Write to a custom database:

```bash
python src/main.py --max-apps 20 --db data/test.db
```

Show all CLI options:

```bash
python src/main.py --help
```

## Output

By default, data is stored at:

```text
data/cafebazaar_results.db
```

The crawler uses `INSERT OR REPLACE` with `(package_name, source)` as the primary key, so the same app is updated rather than duplicated in the database.

Quick record count:

```bash
python -c "import sqlite3; c=sqlite3.connect('data/cafebazaar_results.db'); print(c.execute('select count(*) from app_details').fetchone()[0])"
```

## Configuration

Defaults are intentionally conservative to reduce request pressure. They can be overridden with environment variables:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `CAFEBAZAAR_CATEGORY_DELAY_MS` | `10000` | Delay after each category |
| `CAFEBAZAAR_SUBCATEGORY_DELAY_MS` | `2000` | Delay after each subcategory |
| `CAFEBAZAAR_APP_DELAY_MS` | `100` | Delay after each app |
| `CAFEBAZAAR_DATA_DIR` | `./data` | Output directory |
| `CAFEBAZAAR_DB_PATH` | `./data/cafebazaar_results.db` | Exact SQLite path |

## Database fields

The `app_details` table includes:

`name`, `package_name`, developer contact fields, `homepage_url`, install count, rating statistics, category/subcategory, update timestamp, tags, price, source, descriptions, and version.

## Tests

Run the local unit tests with:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same tests on supported Python versions for pushes and pull requests.

## Operational notes

- The crawler relies on CafeBazaar web API endpoints and response structures, which may change over time.
- Network or upstream changes can cause individual requests to fail; transient failures are retried.
- Pressing `Ctrl+C` stops the crawl without deleting data already written to SQLite.
- Database files and virtual environments are excluded from Git.

## Responsible use

Use this project in accordance with CafeBazaar's terms, applicable laws, and reasonable request rates. This project is not affiliated with or endorsed by CafeBazaar.

## License

MIT — see [LICENSE](LICENSE).
