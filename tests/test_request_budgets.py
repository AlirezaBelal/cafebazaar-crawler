"""Offline regression tests for bounded requests and truthful exit codes."""

import argparse
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bazarService
import config
import main as cli


class PageBudgetTests(unittest.TestCase):
    def test_app_page_budget_one_skips_followup_request(self):
        first = [{"packageName": "com.example.first"}]
        with patch.object(bazarService, "fetch_initial_page", return_value=(first, 1)):
            with patch.object(bazarService, "fetch_next_page") as next_page:
                apps = bazarService.fetch_all_apps("category", max_pages=1)
        self.assertEqual(apps, first)
        next_page.assert_not_called()

    def test_app_page_budget_two_fetches_one_followup(self):
        first = [{"packageName": "com.example.first"}]
        second = [{"packageName": "com.example.second"}]
        with patch.object(bazarService, "fetch_initial_page", return_value=(first, 1)):
            with patch.object(bazarService, "fetch_next_page", return_value=(second, 2)) as next_page:
                with patch.object(bazarService.time, "sleep"):
                    apps = bazarService.fetch_all_apps("category", max_pages=2)
        self.assertEqual(apps, first + second)
        next_page.assert_called_once()

    def test_subcategory_budget_one_never_requests_second_page(self):
        response = MagicMock()
        response.json.return_value = {
            "singleReply": {
                "getPageBodyReply": {"pageBody": {
                    "rows": [{"simpleAppList": {
                        "title": "Weather",
                        "expandInfo": {"vitrinExpandInfo": {"path": "weather/apps"}}
                    }}]
                }}
            }
        }
        session = MagicMock()
        session.post.return_value = response
        with patch.object(bazarService, "get_session", return_value=session):
            with patch.object(bazarService.time, "sleep"):
                result = bazarService.fetch_all_subcategories("weather", max_pages=1)
        self.assertEqual(result, [{"title": "Weather", "path": "weather/apps"}])
        session.post.assert_called_once()


class CommandLineTests(unittest.TestCase):
    def test_rejects_negative_limits(self):
        for option in (
            "--max-apps", "--category-limit", "--subcategory-limit",
            "--max-list-pages", "--max-subcategory-pages",
        ):
            with self.subTest(option=option):
                with patch.object(sys, "argv", ["crawler", option, "-1"]):
                    with patch.object(sys, "stderr"):
                        with self.assertRaises(SystemExit) as error:
                            cli.parse_args()
                self.assertEqual(error.exception.code, 2)

    def test_page_limits_are_forwarded_without_using_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = argparse.Namespace(
                db=str(Path(tmp) / "test.db"),
                max_apps=2, category_limit=1, subcategory_limit=1,
                max_list_pages=2, max_subcategory_pages=1,
            )
            with patch.object(config, "RESULT_FILE", str(Path(tmp) / "test.db")):
                with patch.object(bazarService, "get_cafebazaar_categories",
                                  return_value=[{"title": "Cat", "path": "cat"}]):
                    with patch.object(bazarService, "fetch_all_subcategories",
                                      return_value=[{"title": "Sub", "path": "sub"}]) as subcats:
                        with patch.object(bazarService, "fetch_all_apps",
                                          return_value=[{"packageName": "pkg"}]) as apps:
                            with patch.object(bazarService, "fetch_app_details",
                                              return_value=None):
                                with patch.object(cli, "sleep"):
                                    status = cli.run(args)
            self.assertEqual(status, 1)
            subcats.assert_called_once_with("cat", max_pages=1)
            apps.assert_called_once_with("sub", max_pages=2)


if __name__ == "__main__":
    unittest.main()
