import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bazarService
import config


class BazarServiceTests(unittest.TestCase):
    def test_extract_app_details_persists_tags_and_package(self):
        payload = {
            "singleReply": {
                "appDetailsV2Reply": {
                    "meta": {
                        "name": "Weather App",
                        "tags": [{"title": "weather"}, {"title": "forecast"}],
                        "category": {"slug": "weather"},
                        "installCount": {"range": "۱،۰۰۰+"},
                        "reviewInfo": {"averageRate": 4.5, "reviewCount": 12},
                    },
                    "package": {
                        "name": "com.example.weather",
                        "versionName": "1.0",
                        "lastUpdated": "",
                    },
                }
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            previous_db = config.RESULT_FILE
            config.RESULT_FILE = str(Path(temp_dir) / "results.db")
            try:
                app = bazarService.extract_app_details(payload, "Forecast")
                self.assertEqual(app.package_name, "com.example.weather")
                self.assertEqual(app.tags, ["weather", "forecast"])

                with sqlite3.connect(config.RESULT_FILE) as connection:
                    row = connection.execute(
                        "SELECT package_name, tags FROM app_details"
                    ).fetchone()
                self.assertEqual(row, ("com.example.weather", "weather,forecast"))
            finally:
                config.RESULT_FILE = previous_db


if __name__ == "__main__":
    unittest.main()
