import argparse
import sqlite3
import sys
import traceback
from pathlib import Path
from time import sleep

import config
from local_report import create_demo, create_report, export_csv


def parse_args():
    parser = argparse.ArgumentParser(
        description="Crawl CafeBazaar app metadata and store it in SQLite."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--demo",
        action="store_true",
        help="Generate synthetic demo data and an offline HTML report (no network).",
    )
    mode.add_argument(
        "--report",
        metavar="REPORT.html",
        help="Create a searchable offline HTML report from --db (no network).",
    )
    mode.add_argument(
        "--export-csv",
        metavar="APPS.csv",
        help="Export selected SQLite metadata fields to a safe CSV (no network).",
    )
    mode.add_argument(
        "--full",
        action="store_true",
        help="Explicitly request a full, unbounded network crawl.",
    )
    parser.add_argument(
        "--report-limit",
        type=int,
        default=500,
        help="Maximum rows included in a local HTML report (1..1000).",
    )
    parser.add_argument(
        "--max-apps",
        type=int,
        default=0,
        help="Stop after this many successfully fetched apps (0 = unlimited).",
    )
    parser.add_argument(
        "--category-limit",
        type=int,
        default=0,
        help="Process only the first N categories (0 = unlimited).",
    )
    parser.add_argument(
        "--subcategory-limit",
        type=int,
        default=0,
        help="Process only the first N subcategories per category (0 = unlimited).",
    )
    parser.add_argument(
        "--max-list-pages",
        type=int,
        default=0,
        help="Maximum listing API pages per subcategory (0 = unlimited).",
    )
    parser.add_argument(
        "--max-subcategory-pages",
        type=int,
        default=0,
        help="Maximum subcategory API pages per category (0 = unlimited).",
    )
    parser.add_argument(
        "--db",
        default=config.RESULT_FILE,
        help="SQLite output path. Defaults to data/cafebazaar_results.db.",
    )
    args = parser.parse_args()
    if not 1 <= args.report_limit <= 1000:
        parser.error("--report-limit must be between 1 and 1000")
    for name in ("max_apps", "category_limit", "subcategory_limit",
                 "max_list_pages", "max_subcategory_pages"):
        if getattr(args, name) < 0:
            parser.error("--" + name.replace("_", "-") + " must be non-negative (0 = unlimited)")
    return args


def limited(items, limit):
    return items[:limit] if limit and limit > 0 else items


def print_summary(stats):
    print("\n=== CRAWL SUMMARY ===")
    print(f"Categories processed:    {stats['categories']}")
    print(f"Subcategories processed: {stats['subcategories']}")
    print(f"Apps saved:              {stats['saved']}")
    print(f"Apps failed:             {stats['failed']}")
    print(f"Duplicates skipped:      {stats['duplicates']}")
    print(f"Database:                {config.RESULT_FILE}")


def run(args):
    # Import network-only dependencies only when a real crawl is requested.
    import bazarService
    db_path = Path(args.db).expanduser().resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    config.RESULT_FILE = str(db_path)

    stats = {
        "categories": 0,
        "subcategories": 0,
        "saved": 0,
        "failed": 0,
        "duplicates": 0,
    }
    seen_packages = set()

    print("=== CafeBazaar Crawler ===")
    print(f"Database: {config.RESULT_FILE}")
    print("Fetching categories...")

    categories = bazarService.get_cafebazaar_categories()
    if not categories:
        print("No categories were returned. Nothing to crawl.")
        print_summary(stats)
        return 1

    try:
        for category in limited(categories, args.category_limit):
            stats["categories"] += 1
            title = category.get("title") or "unknown"
            path = category.get("path")
            if not path:
                continue

            print(f"\n[Category] {title}")
            subcategories = bazarService.fetch_all_subcategories(
                path, max_pages=args.max_subcategory_pages
            )

            for subcategory in limited(subcategories, args.subcategory_limit):
                stats["subcategories"] += 1
                config.DEVICE_ID = config.generate_random_string()

                sub_title = subcategory.get("title") or "unknown"
                sub_path = subcategory.get("path")
                if not sub_path:
                    continue

                print(f"  [Subcategory] {sub_title}")
                apps = bazarService.fetch_all_apps(
                    sub_path, max_pages=args.max_list_pages
                )
                print(f"  Found {len(apps)} apps")

                for app in apps:
                    if args.max_apps > 0 and stats["saved"] >= args.max_apps:
                        print_summary(stats)
                        return 1 if stats["failed"] else 0

                    package_name = app.get("packageName")
                    if not package_name:
                        stats["failed"] += 1
                        continue

                    if package_name in seen_packages:
                        stats["duplicates"] += 1
                        continue
                    seen_packages.add(package_name)

                    try:
                        app_detail = bazarService.fetch_app_details(package_name, sub_title)
                        if app_detail is None:
                            stats["failed"] += 1
                            print(f"    [FAILED] {package_name}")
                        else:
                            stats["saved"] += 1
                            print(f"    [SAVED] {app_detail.package_name}")
                            if args.max_apps > 0 and stats["saved"] >= args.max_apps:
                                print_summary(stats)
                                return 1 if stats["failed"] else 0
                    except Exception as exc:
                        stats["failed"] += 1
                        print(f"    [ERROR] {package_name}: {exc}")
                        traceback.print_exc()

                    sleep(config.SLEEP_AFTER_EACH_APPS_IN_MILL_SECONDS / 1000)

                sleep(config.SLEEP_AFTER_EACH_SUB_CATEGORIES_IN_MILL_SECONDS / 1000)

            sleep(config.SLEEP_AFTER_EACH_CATEGORIES_IN_MILL_SECONDS / 1000)

    except KeyboardInterrupt:
        print("\nCrawl stopped by user. Saved data is kept in SQLite.")
        print_summary(stats)
        return 130

    print_summary(stats)
    # Empty or partially failed crawls must not report success to automation.
    return 0 if stats["saved"] > 0 and stats["failed"] == 0 else 1


def main():
    args = parse_args()
    try:
        if args.demo:
            # Never mix synthetic app records into the default real-data database.
            db_path = (Path(args.db) if args.db != config.RESULT_FILE
                       else config.DATA_DIR / "demo.db")
            count = create_demo(db_path)
            report_path = db_path.with_name(db_path.stem + "-report.html")
            create_report(db_path, report_path, args.report_limit)
            print("Created {} synthetic DEMO apps in {}".format(count, db_path))
            print("Open the local HTML report:", report_path)
            return 0
        if args.report:
            count = create_report(Path(args.db), Path(args.report), args.report_limit)
            print("Wrote an offline HTML report with {} apps to {}".format(count, args.report))
            return 0
        if args.export_csv:
            count = export_csv(Path(args.db), Path(args.export_csv))
            print("Exported {} apps to {}".format(count, args.export_csv))
            return 0
        if not args.full and not any((
            args.max_apps, args.category_limit, args.subcategory_limit,
            args.max_list_pages, args.max_subcategory_pages,
        )):
            print("No network request made. Try --demo or run a bounded crawl:")
            print("python src/main.py --category-limit 1 --subcategory-limit 1 "
                  "--max-apps 5 --max-list-pages 1 --max-subcategory-pages 1")
            print("Use --full only after confirming that unlimited crawling is appropriate.")
            return 0
        return run(args)
    except (FileExistsError, ValueError, OSError, sqlite3.DatabaseError) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
