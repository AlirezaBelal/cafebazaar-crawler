# cafebazaar-crawler

A powerful tool for collecting and extracting data from the CafeBazaar Android app store, Iran's largest application marketplace.

## Description

CafeBazaarCrawler is a Python script that systematically extracts all categories, subcategories, and applications available in the CafeBazaar app store and collects detailed information about each application. This information includes the name, package name, category, developer, number of installations, rating, number of reviews, and price.

CafeBazaar is the largest Android application marketplace in Iran with over 40 million users and controlling around 75-97% of the Iranian Android app market. The platform offers thousands of Iranian and international applications, with a focus on delivering content to Persian-speaking users.

## Features

- Extract all categories available in CafeBazaar
- Extract all subcategories of each category
- Collect the list of applications in each subcategory
- Extract complete information for each application including:
  - Basic details (name, package name, version)
  - Developer information (author name, email, homepage)
  - Statistics (installation count, ratings, review counts)
  - Content information (descriptions, categories, tags)
- Support for pagination to receive all data
- Store data in an SQLite database with proper indexing
- Generate a random device ID for each request
- Apply delays between requests to prevent blocking

## Prerequisites

- Python 3.7+
- Required packages in `requirements.txt`:
  - requests
  - jdatetime (for Persian calendar conversion)
  - typing
  - sqlite3 (included in Python standard library)

## Installation

1. Clone the repository:
```
git clone https://github.com/AlirezaBelal/cafebazaar-crawler.git
cd cafebazaar-crawler
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Make sure the required modules are installed:
```
pip install requests
```

## Configuration

The main settings are located in the `config.py` file:

- `DEVICE_ID`: Device ID for requests (automatically generated)
- `SLEEP_AFTER_EACH_CATEGORIES_IN_MILL_SECONDS`: Delay between category requests (milliseconds)
- `SLEEP_AFTER_EACH_SUB_CATEGORIES_IN_MILL_SECONDS`: Delay between subcategory requests (milliseconds)
- `SLEEP_AFTER_EACH_APPS_IN_MILL_SECONDS`: Delay between application requests (milliseconds)
- `RESULT_FILE`: Path to the database file for storing results

## Usage

To run the script:

```
python src/main.py
```

This command:
1. Extracts all categories available in CafeBazaar
2. For each category, extracts all subcategories
3. For each subcategory, extracts the complete list of applications
4. For each application, extracts its complete information and stores it in the database

## Notes

- The use of this tool must comply with CafeBazaar's terms of service.
- To prevent IP blocking, adjust the delay settings according to your needs.
- This tool is designed for educational and research purposes only.

## Contributing

Your suggestions and contributions help improve this project. Please create a new Issue or submit a Pull Request to contribute.

## License

This project is published under the MIT license. For more information, read the `LICENSE` file.

## About CafeBazaar

CafeBazaar (کافه بازار) is the largest Android app store in Iran, established in 2011. It serves as an alternative to Google Play, which has had limited availability in Iran at various times. The platform focuses on Persian-speaking users, providing both local Iranian apps and international applications.