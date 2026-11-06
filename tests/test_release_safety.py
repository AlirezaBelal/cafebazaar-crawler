"""Release safety regressions; all API responses and databases are synthetic."""
import argparse
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import bazarService as service
import config
import main
import local_report as report


class ReleaseSafetyTests(unittest.TestCase):
    def test_recovery_files_are_not_export_destinations(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / 'apps.db'
            report.create_demo(db)
            for suffix in ('-wal', '-shm', '-journal'):
                target = Path(str(db) + suffix)
                target.write_bytes(b'recovery bytes')
                for exporter in (report.export_csv, report.create_report):
                    with self.assertRaises(ValueError):
                        exporter(db, target)
                    self.assertEqual(target.read_bytes(), b'recovery bytes')

    def test_failed_export_preserves_previous_output_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'out.csv'
            target.write_text('previous', encoding='utf-8')
            with self.assertRaises(OSError):
                with report._atomic_output(target, 'utf-8') as handle:
                    handle.write('partial')
                    raise OSError('synthetic write failure')
            self.assertEqual(target.read_text(), 'previous')
            self.assertEqual(list(Path(folder).iterdir()), [target])

    def test_mismatched_response_cannot_create_database(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / 'never-created.db'
            with patch.object(config, 'RESULT_FILE', str(db)):
                with self.assertRaises(ValueError):
                    service.extract_app_details({'singleReply': {'appDetailsV2Reply': {
                        'package': {'name': 'org.example.other'}}}}, 'test', 'org.example.requested')
            self.assertFalse(db.exists())

    def test_refusal_does_not_retry_details(self):
        for status in (401, 403, 429):
            with patch.object(service, '_post', return_value=Mock(status_code=status)) as post:
                with patch.object(service.time, 'sleep') as sleep:
                    self.assertIsNone(service.fetch_app_details('org.example.app', 'test'))
            post.assert_called_once()
            sleep.assert_not_called()

    def test_invalid_package_never_requests(self):
        with patch.object(service, '_post') as post:
            with self.assertRaises(ValueError):
                service.fetch_app_details('../invalid', 'test')
        post.assert_not_called()

    def test_partial_and_empty_runs_are_nonzero_including_app_limit(self):
        for max_apps, outcomes in ((1, [None, Mock(package_name='org.example.two')]),
                                    (0, [None, Mock(package_name='org.example.two')]),
                                    (0, [])):
            with tempfile.TemporaryDirectory() as folder:
                args = argparse.Namespace(db=str(Path(folder) / 'test.db'), max_apps=max_apps,
                    category_limit=1, subcategory_limit=1, max_list_pages=1, max_subcategory_pages=1)
                apps = [{'packageName': 'org.example.' + str(i)} for i in range(len(outcomes))]
                with patch.object(config, 'RESULT_FILE', args.db), \
                     patch.object(service, 'get_cafebazaar_categories', return_value=[{'path':'cat'}]), \
                     patch.object(service, 'fetch_all_subcategories', return_value=[{'path':'sub'}]), \
                     patch.object(service, 'fetch_all_apps', return_value=apps), \
                     patch.object(service, 'fetch_app_details', side_effect=outcomes), \
                     patch.object(main, 'sleep'):
                    self.assertEqual(main.run(args), 1)
