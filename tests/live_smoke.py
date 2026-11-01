"""Opt-in, one-app end-to-end smoke test against CafeBazaar's public API.

Runs only when called with --yes-live. Never part of automated CI.
Uses a disposable SQLite database and limits every listing to a single page.
"""
import argparse
from contextlib import closing
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bazarService
import config


def main():
    parser = argparse.ArgumentParser(description="Small live CafeBazaar API smoke test")
    parser.add_argument(
        "--yes-live", action="store_true",
        help="I confirm this test may make a few public API requests.",
    )
    args = parser.parse_args()
    if not args.yes_live:
        parser.error("Live network testing requires explicit --yes-live")
    with tempfile.TemporaryDirectory(prefix="cafebazaar-smoke-") as folder:
        original = config.RESULT_FILE
        config.RESULT_FILE = str(Path(folder) / "smoke.db")
        try:
            categories = bazarService.get_cafebazaar_categories()
            paths = [item.get("path") for item in categories if item.get("path")]
            if not paths:
                raise RuntimeError("No usable category returned; API may have changed or access may be restricted")
            time.sleep(1.5)
            subcats = bazarService.fetch_all_subcategories(paths[0], max_pages=1)
            paths = [item.get("path") for item in subcats if item.get("path")]
            if not paths:
                raise RuntimeError("No usable subcategories from the first category")
            time.sleep(1.5)
            apps = bazarService.fetch_all_apps(paths[0], max_pages=1)
            packages = [item.get("packageName") for item in apps if item.get("packageName")]
            if not packages:
                raise RuntimeError("No app packages from the first listing page")
            time.sleep(1.5)
            app = bazarService.fetch_app_details(packages[0], "smoke-test")
            if app is None or app.package_name != packages[0] or not app.name.strip():
                raise RuntimeError("App detail API was unavailable or incomplete")
            with closing(sqlite3.connect(config.RESULT_FILE)) as connection:
                stored = connection.execute(
                    "SELECT package_name, name FROM app_details WHERE package_name = ?",
                    (packages[0],),
                ).fetchone()
            if not stored:
                raise RuntimeError("Fetched app was not saved to the temporary SQLite database")
            print("LIVE_SMOKE_PASS: categories, listings, app detail and SQLite write")
            print("One public app verified. No dataset was retained.")
            return 0
        except (RuntimeError, ValueError, OSError) as exc:
            print("LIVE_SMOKE_FAIL:", exc, file=sys.stderr)
            return 1
        finally:
            config.RESULT_FILE = original


if __name__ == "__main__":
    raise SystemExit(main())
