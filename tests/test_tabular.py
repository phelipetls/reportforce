import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402
from utils import mocks  # noqa: E402

metadata = mocks.get_json("analytics_tabular_metadata")
report = mocks.get_json("analytics_tabular")


class TestTabularReport(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):

        mocked_report = report
        mocked_metadata.return_value = metadata

        with patch.dict(mocked_report, values=mocked_report, allData=False, clear=True):
            mocked_request().json.side_effect = [mocked_report] * 2

            self.report = get_report(
                "report_id", id_column="Opportunity Name", session=mocks.FakeLogin
            )

    def test_columns(self):
        test = self.report.columns.tolist()
        expected = [
            "Opportunity Name",
            "Amount",
            "Lead Source",
            "Next Step",
            "Probability (%)",
            "Fiscal Period",
            "Age",
            "Created Date",
            "Opportunity Owner",
            "Owner Role",
        ]
        self.assertListEqual(test, expected)

    def test_length(self):
        test = len(self.report)
        expected = 2
        self.assertEqual(test, expected)


class TestEmptyTabular(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):

        mocked_metadata.return_value = metadata

        mocked_factmap = {"T!T": {"aggregates": {"label": 0, "value": 0}, "rows": []}}

        with patch.dict(report, values=report, factMap = mocked_factmap):
            mocked_request().json.return_value = report

            self.report = get_report(
                "report_id", id_column="Opportunity Name", session=mocks.FakeLogin
            )

    def test_empty_report(self):
        self.assertTrue(self.report.empty)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
