import argparse
import traceback
from pathlib import Path
from time import sleep

import bazarService
import config


def parse_args():
    parser = argparse.ArgumentParser(
        description="Crawl CafeBazaar app metadata and store it in SQLite."
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
        "--db",
        default=config.RESULT_FILE,
        help="SQLite output path. Defaults to data/cafebazaar_results.db.",
    )
    return parser.parse_args()


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
            subcategories = bazarService.fetch_all_subcategories(path)

            for subcategory in limited(subcategories, args.subcategory_limit):
                stats["subcategories"] += 1
                config.DEVICE_ID = config.generate_random_string()

                sub_title = subcategory.get("title") or "unknown"
                sub_path = subcategory.get("path")
                if not sub_path:
                    continue

                print(f"  [Subcategory] {sub_title}")
                apps = bazarService.fetch_all_apps(sub_path)
                print(f"  Found {len(apps)} apps")

                for app in apps:
                    if args.max_apps > 0 and stats["saved"] >= args.max_apps:
                        print_summary(stats)
                        return 0

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
                                return 0
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
    return 0


def main():
    args = parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
