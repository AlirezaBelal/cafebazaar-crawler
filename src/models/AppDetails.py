import sqlite3
from enum import Enum
from typing import List, Dict
from datetime import datetime, timedelta, timezone
import jdatetime
import re

class Source(Enum):
    BAZAR = "bazar"
    MYKET = "myket"

class AppDetails:
    def __init__(self, name: str = '', package_name: str = '', author_name: str = '', author_phone_number: str = '',
                 author_email: str = '', installation_count: int = 10000, average_score: float = 0.0, comment_count: int = 0,
                 star_1_count: int = 0, star_2_count: int = 0, star_3_count: int = 0, star_4_count: int = 0, star_5_count: int = 0,
                 category: str = '', sub_category: str = '', last_update: int = 0, tags: List[str] = None, price: int = 0,
                 source: Source = Source.BAZAR, short_description: str = '',long_description: str = '',homepageUrl:str = '',version: str = ''):
        if tags is None:
            tags = []
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
        self.tags = tags
        self.price = price
        self.source = source
        self.short_description = short_description
        self.long_description = long_description
        self.homepageUrl = homepageUrl
        self.version = version

    @classmethod
    def from_dict(cls, data: Dict, source: Source, tags: List[str],subcategory):
        meta = data.get('meta', {})
        package = data.get('package', {})

        # Convert installation count to an integer
        install_count_str = meta.get('installCount', {}).get('range', '0')
        install_count = cls.parse_installation_count(install_count_str)

        # Parse Jalali date to epoch time
        last_update_str = package.get('lastUpdated', '')
        last_update_epoch = cls.parse_jalali_to_epoch(last_update_str)

        return cls(
            name=meta.get('name', ''),
            package_name=package.get('name', ''),
            author_name=meta.get('author', {}).get('name', ''),
            author_phone_number=meta.get('phoneNumber', ''),
            author_email=meta.get('email', ''),
            installation_count=install_count,
            average_score=meta.get('reviewInfo', {}).get('averageRate', 0.0),
            comment_count=meta.get('reviewInfo', {}).get('reviewCount', 0),
            star_1_count=meta.get('reviewInfo', {}).get('rate1Count', 0),
            star_2_count=meta.get('reviewInfo', {}).get('rate2Count', 0),
            star_3_count=meta.get('reviewInfo', {}).get('rate3Count', 0),
            star_4_count=meta.get('reviewInfo', {}).get('rate4Count', 0),
            star_5_count=meta.get('reviewInfo', {}).get('rate5Count', 0),
            category=meta.get('category', {}).get('slug', ''),
            sub_category=subcategory,
            last_update=last_update_epoch,
            tags=tags,
            price=meta.get('payment', {}).get('price', 0),
            source=source,
            short_description=meta.get('shortDescription', ''),
            long_description=meta.get('description', ''),
            homepageUrl=meta.get('homepageUrl', ''),
            version=package.get('versionName', ''),
        )

    @staticmethod
    def parse_installation_count(install_count_str: str) -> int:
        persian_to_english_digits = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        install_count_str_translated = install_count_str.translate(persian_to_english_digits)
        install_count_str_clean = re.sub(r'[^0-9]', '', install_count_str_translated)
        try:
            return int(install_count_str_clean)
        except ValueError:
            return 0

    @staticmethod
    def parse_jalali_to_epoch(jalali_str: str) -> int:
        try:
            jalali_date = jdatetime.datetime.strptime(jalali_str, '%d %B %Y')
            gregorian_date = jalali_date.togregorian()
            tehran_tz = timezone(timedelta(hours=3, minutes=30))
            tehran_time = gregorian_date.replace(tzinfo=tehran_tz)
            return int(tehran_time.timestamp())
        except ValueError:
            return 0

    def save_to_db(self, db_name='app_details.db'):
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute('''
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
        ''')

        # Create indices for package_name and installation_count
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_package_name ON app_details (package_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_installation_count ON app_details (installation_count)')

        # Insert data into the table
        cursor.execute('''
            INSERT OR REPLACE INTO app_details (
                name, package_name, author_name, author_phone_number, author_email,homepage_url,
                installation_count, average_score, comment_count, star_1_count,
                star_2_count, star_3_count, star_4_count, star_5_count, category,
                sub_category, last_update, tags, price, source, short_description, long_description, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?,?,?)
        ''', (
            self.name, self.package_name, self.author_name, self.author_phone_number,
            self.author_email,self.homepageUrl, self.installation_count, self.average_score,
            self.comment_count, self.star_1_count, self.star_2_count, self.star_3_count,
            self.star_4_count, self.star_5_count, self.category, self.sub_category,
            self.last_update, ','.join(self.tags), self.price, self.source.value,
            self.short_description, self.long_description, self.version
        ))

        connection.commit()
        connection.close()

# Example usage
data_dict = {
    'meta': {
        'name': 'زلزله نگار زامیاد - هشدار زمین لرزه',
        'email': 'dev@syncrex.me',
        'phoneNumber': '',
        'homepageUrl': 'https://syncrex.me',
        'shortDescription': 'زلزله نگار, هشدار زلزله، زلزله های اطراف من، آخرین زلزله ها، اخبار زلزله ها، زمین‌لرزه، ردیاب زلزله، زامیاد',
        'description': '<p><p>زلزله نگار زامیاد <br> </p> <p>زامیاد یک اپلیکیشن ردیاب زلزله است که با ظاهری زیبا و جذاب امکانات ویژه ای را در اختیار شما قرار می دهد.</p>',
        'hasInAppPurchase': False,
        'contentRatingInfo': {'rating': '', 'tinyImage': ''},
        'author': {'name': 'سینکرس', 'slug': '294016635252'},
        'reviewInfo': {'averageRate': 4.7, 'rate1Count': 8, 'rate2Count': 5, 'rate3Count': 5, 'rate4Count': 24, 'rate5Count': 224, 'reviewCount': 266, 'verboseReviewCount': '۲۶۶'},
        'payment': {'price': 0, 'priceBeforeDiscount': -1, 'priceString': '۰ تومان', 'priceBeforeDiscountString': '۰ تومان'},
        'category': {'name': 'ابزارها', 'slug': 'tools'},
        'installCount': {'range': '۱۰،۰۰۰+', 'verboseRange': '+۱۰', 'verboseRangeLabel': 'هزار', 'verboseRangeDescription': 'نصب'},
        'tags': [{'title': 'ابزارها', 'vitrinExpandInfo': {'path': 'category/?cat=tools'}}]
    },
    'package': {
        'id': 8981566,
        'name': 'me.syncrex.earthquaketracker',
        'size': '14894155',
        'verboseSize': '۱۴',
        'verboseSizeLabel': 'مگابایت',
        'versionCode': 124,
        'versionName': '۴.۲۴',
        'changeLog': '<p>بهینه سازی جزئی</p>',
        'lastUpdated': '۱۹ شهریور ۱۴۰۳'
    }
}

# # Assuming tags are provided separately, and source is determined based on external input
# tags = [tag.get('title', '') for tag in data_dict.get('meta', {}).get('tags', [])]
# source = Source.BAZAR
#
# app_from_dict = AppDetails.from_dict(data_dict, source, tags)
# app_from_dict.save_to_db("result.db")
# print(app_from_dict)
