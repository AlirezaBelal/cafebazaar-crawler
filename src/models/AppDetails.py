import re
import sqlite3
from datetime import timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List



class Source(Enum):
    BAZAR = "bazar"
    MYKET = "myket"


class AppDetails:
    def __init__(
        self,
        name: str = "",
        package_name: str = "",
        author_name: str = "",
        author_phone_number: str = "",
        author_email: str = "",
        installation_count: int = 0,
        average_score: float = 0.0,
        comment_count: int = 0,
        star_1_count: int = 0,
        star_2_count: int = 0,
        star_3_count: int = 0,
        star_4_count: int = 0,
        star_5_count: int = 0,
        category: str = "",
        sub_category: str = "",
        last_update: int = 0,
        tags: List[str] = None,
        price: int = 0,
        source: Source = Source.BAZAR,
        short_description: str = "",
        long_description: str = "",
        homepageUrl: str = "",
        version: str = "",
    ):
        self.name = name
        self.package_name = package_name
        self.author_name = author_name
        self.author_phone_number = author_phone_number
        self.author_email = author_email
        self.installation_count = installation_count
        self.average_score = average_score
        self.comment_count = comment_count
        self.star_1_count = star_1_count
        self.star_2_count = star_2_count
        self.star_3_count = star_3_count
        self.star_4_count = star_4_count
        self.star_5_count = star_5_count
        self.category = category
        self.sub_category = sub_category
        self.last_update = last_update
        self.tags = tags or []
        self.price = price
        self.source = source
        self.short_description = short_description
        self.long_description = long_description
        self.homepageUrl = homepageUrl
        self.version = version

    @classmethod
    def from_dict(cls, data: Dict, source: Source, tags: List[str], subcategory: str):
        meta = data.get("meta", {})
        package = data.get("package", {})

        install_count = cls.parse_installation_count(
            meta.get("installCount", {}).get("range", "0")
        )
        last_update_epoch = cls.parse_jalali_to_epoch(package.get("lastUpdated", ""))

        return cls(
            name=meta.get("name", ""),
            package_name=package.get("name", ""),
            author_name=meta.get("author", {}).get("name", ""),
            author_phone_number=meta.get("phoneNumber", ""),
            author_email=meta.get("email", ""),
            installation_count=install_count,
            average_score=meta.get("reviewInfo", {}).get("averageRate", 0.0),
            comment_count=meta.get("reviewInfo", {}).get("reviewCount", 0),
            star_1_count=meta.get("reviewInfo", {}).get("rate1Count", 0),
            star_2_count=meta.get("reviewInfo", {}).get("rate2Count", 0),
            star_3_count=meta.get("reviewInfo", {}).get("rate3Count", 0),
            star_4_count=meta.get("reviewInfo", {}).get("rate4Count", 0),
            star_5_count=meta.get("reviewInfo", {}).get("rate5Count", 0),
            category=meta.get("category", {}).get("slug", ""),
            sub_category=subcategory,
            last_update=last_update_epoch,
            tags=tags,
            price=meta.get("payment", {}).get("price", 0),
            source=source,
            short_description=meta.get("shortDescription", ""),
            long_description=meta.get("description", ""),
            homepageUrl=meta.get("homepageUrl", ""),
            version=package.get("versionName", ""),
        )

    @staticmethod
    def parse_installation_count(install_count_str: str) -> int:
        persian_to_english_digits = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
        translated = install_count_str.translate(persian_to_english_digits)
        digits_only = re.sub(r"[^0-9]", "", translated)
        try:
            return int(digits_only)
        except ValueError:
            return 0

    @staticmethod
    def parse_jalali_to_epoch(jalali_str: str) -> int:
        if not jalali_str:
            return 0

        try:
            import jdatetime

            jalali_date = jdatetime.datetime.strptime(jalali_str, "%d %B %Y")
            gregorian_date = jalali_date.togregorian()
            tehran_tz = timezone(timedelta(hours=3, minutes=30))
            tehran_time = gregorian_date.replace(tzinfo=tehran_tz)
            return int(tehran_time.timestamp())
        except (TypeError, ValueError):
            return 0

    def save_to_db(self, db_name="app_details.db"):
        db_path = Path(db_name)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS app_details (
                    name TEXT,
                    package_name TEXT,
                    author_name TEXT,
                    author_phone_number TEXT,
                    author_email TEXT,
                    homepage_url TEXT,
                    installation_count INTEGER,
                    average_score REAL,
                    comment_count INTEGER,
                    star_1_count INTEGER,
                    star_2_count INTEGER,
                    star_3_count INTEGER,
                    star_4_count INTEGER,
                    star_5_count INTEGER,
                    category TEXT,
                    sub_category TEXT,
                    last_update INTEGER,
                    tags TEXT,
                    price INTEGER,
                    source TEXT,
                    short_description TEXT,
                    long_description TEXT,
                    version TEXT,
                    PRIMARY KEY (package_name, source)
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_installation_count "
                "ON app_details (installation_count)"
            )
            cursor.execute(
                """
                INSERT OR REPLACE INTO app_details (
                    name, package_name, author_name, author_phone_number, author_email,
                    homepage_url, installation_count, average_score, comment_count,
                    star_1_count, star_2_count, star_3_count, star_4_count, star_5_count,
                    category, sub_category, last_update, tags, price, source,
                    short_description, long_description, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.name,
                    self.package_name,
                    self.author_name,
                    self.author_phone_number,
                    self.author_email,
                    self.homepageUrl,
                    self.installation_count,
                    self.average_score,
                    self.comment_count,
                    self.star_1_count,
                    self.star_2_count,
                    self.star_3_count,
                    self.star_4_count,
                    self.star_5_count,
                    self.category,
                    self.sub_category,
                    self.last_update,
                    ",".join(self.tags),
                    self.price,
                    self.source.value,
                    self.short_description,
                    self.long_description,
                    self.version,
                ),
            )
