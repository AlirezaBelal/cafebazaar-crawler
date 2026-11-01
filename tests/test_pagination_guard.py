"""Pagination regression tests using synthetic API pages and no network."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bazarService


class PaginationGuardTests(unittest.TestCase):
    def test_repeated_app_page_stops_without_collecting_duplicates(self):
        first = [{"packageName": "com.example.one"}]
        next_page = [{"packageName": "com.example.two"}]
        with patch.object(bazarService, "fetch_initial_page", return_value=(first, 1)):
            with patch.object(bazarService, "fetch_next_page", side_effect=[
                (next_page, 2), (first, 3),
            ]) as fetch_next:
                with patch.object(bazarService.time, "sleep"):
                    apps = bazarService.fetch_all_apps("test/category")

        self.assertEqual([app["packageName"] for app in apps], [
            "com.example.one", "com.example.two",
        ])
        self.assertEqual(fetch_next.call_count, 2)

    def test_repeated_subcategory_page_stops_before_third_request(self):
        response = MagicMock()
        response.json.return_value = {
            "singleReply": {
                "getPageBodyReply": {
                    "pageBody": {
                        "rows": [{
                            "simpleAppList": {
                                "title": "Utilities",
                                "expandInfo": {
                                    "vitrinExpandInfo": {"path": "apps/utilities"}
                                },
                            }
                        }]
                    }
                }
            }
        }
        session = MagicMock()
        session.post.return_value = response
        with patch.object(bazarService, "get_session", return_value=session):
            with patch.object(bazarService.time, "sleep"):
                subcategories = bazarService.fetch_all_subcategories("apps")

        self.assertEqual(subcategories, [
            {"title": "Utilities", "path": "apps/utilities"},
        ])
        self.assertEqual(session.post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
