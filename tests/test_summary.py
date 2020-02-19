import os
import sys
import unittest
import itertools

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402
from utils import mocks  # noqa: E402

metadata = mocks.get_json("analytics_summary_metadata")
report = mocks.get_json("analytics_summary")


class TestSummaryReport(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):

        mocked_report = report
        mocked_metadata.return_value = metadata

        with patch.dict(mocked_report, values=mocked_report, allData=False, clear=True):
            mocked_request().json.side_effect = [mocked_report] * 2

            self.report = get_report("report_id", id_column="label1", session=mocks.FakeLogin)

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


class TestEmptySummary(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):

        mocked_report = report
        mocked_metadata.return_value = metadata

        mocked_report = mocks.get_json("analytics_summary")
        mocked_factmap = {'factMap': {'T!T': {'aggregates': {'label': 0, 'value': 0}}}}

        with patch.dict(mocked_report, mocked_factmap):
            mocked_request().json.return_value = mocked_report

            self.report = get_report("report_id", id_column="label1", session=mocks.FakeLogin)

    def test_if_report_is_empty(self):
        self.assertTrue(self.report.empty)


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
