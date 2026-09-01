import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from models.AppDetails import AppDetails, Source


class AppDetailsTests(unittest.TestCase):
    def test_parse_persian_installation_count(self):
        self.assertEqual(AppDetails.parse_installation_count("۱۰،۰۰۰+"), 10000)

    def test_database_upsert_keeps_one_row_per_package_and_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "results.db"

            AppDetails(
                name="First",
                package_name="com.example.app",
                source=Source.BAZAR,
            ).save_to_db(db_path)
            AppDetails(
                name="Updated",
                package_name="com.example.app",
                source=Source.BAZAR,
            ).save_to_db(db_path)

            with sqlite3.connect(db_path) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM app_details"
                ).fetchone()[0]
                name = connection.execute(
                    "SELECT name FROM app_details WHERE package_name = ?",
                    ("com.example.app",),
                ).fetchone()[0]

            self.assertEqual(count, 1)
            self.assertEqual(name, "Updated")


if __name__ == "__main__":
    unittest.main()
