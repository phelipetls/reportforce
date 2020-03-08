import os
import sys
import unittest
import itertools

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import Reportforce  # noqa: E402

report = mocks.get_json("analytics_summary")

class TestSummaryReport(unittest.TestCase):
    @patch.object(Reportforce.session, "post")
    def setUp(self, post):
        mocks.mock_get_metadata("analytics_summary_metadata").start()
        mocks.mock_login().start()

        post().json.side_effect = mocks.generate_reports(report)

        rf = Reportforce("foo@bar.com", "1234", "XXX")
        self.report = rf.get_report("report_id", id_column="label1")

    def test_summary_length(self):
        length = len(self.report)
        expected_length = 324
        self.assertEqual(length, expected_length)

    def test_summary_index(self):
        index = self.report.index.tolist()
        expected_index = itertools.chain.from_iterable([[("label",) * 3] * 324])
        self.assertListEqual(index, list(expected_index))

    def test_summary_columns(self):
        columns = self.report.columns.tolist()
        expected_columns = [
            "label1",
            "label2",
            "label3",
            "label4",
            "label5",
            "label6",
            "label7",
        ]
        self.assertEqual(columns, expected_columns)

    @patch.object(Reportforce.session, "post")
    def test_if_report_is_empty(self, post):

        mock_factmap = {"factMap": {"T!T": {"aggregates": {"label": 0, "value": 0}}}}

        with patch.dict(report, mock_factmap):
            post().json.return_value = report

            rf = Reportforce("foo@bar.com", "1234", "XXX")
            self.report = rf.get_report("report_id", id_column="label1")

        self.assertTrue(self.report.empty)


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
