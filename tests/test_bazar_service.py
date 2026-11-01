import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bazarService
import config


class BazarServiceTests(unittest.TestCase):
    def test_request_session_is_closed_on_success_and_failure(self):
        from unittest.mock import Mock, patch
        for failure in (None, OSError("connection failed")):
            session = Mock()
            session.post.side_effect = failure
            with patch.object(bazarService, "get_session", return_value=session):
                if failure:
                    with self.assertRaises(OSError):
                        bazarService._post("https://example.test", timeout=30)
                else:
                    self.assertIs(bazarService._post("https://example.test", timeout=30),
                                  session.post.return_value)
            session.close.assert_called_once()

    def test_malformed_subcategory_responses_stop_after_three_attempts(self):
        from unittest.mock import Mock, patch
        session = Mock()
        session.post.return_value.json.return_value = {"singleReply": None}
        with patch.object(bazarService, "get_session", return_value=session), \
                patch.object(bazarService.time, "sleep"):
            self.assertEqual(bazarService.fetch_all_subcategories("test"), [])
        self.assertEqual(session.post.call_count, 3)

    def test_missing_package_is_rejected_without_creating_database(self):
        with tempfile.TemporaryDirectory() as folder:
            from unittest.mock import patch
            database = Path(folder) / "invalid.db"
            with patch.object(config, "RESULT_FILE", str(database)):
                for reply in ({}, {"package": {}}, {"package": None}):
                    with self.assertRaises(ValueError):
                        bazarService.extract_app_details(
                            {"singleReply": {"appDetailsV2Reply": reply}}, "test")
            self.assertFalse(database.exists())

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

                connection = sqlite3.connect(config.RESULT_FILE)
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT package_name, tags FROM app_details")
                    row = cursor.fetchone()
                finally:
                    cursor.close()
                    connection.close()

                self.assertEqual(row, ("com.example.weather", "weather,forecast"))
            finally:
                config.RESULT_FILE = previous_db


if __name__ == "__main__":
    unittest.main()
