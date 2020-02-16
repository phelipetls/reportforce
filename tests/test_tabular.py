import os
import sys
import json
import unittest

from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402


class FakeLogin:
    """Fake Salesforce session object"""

    version = "47.0"
    session_id = "sessionId"
    instance_url = "dummy.salesforce.com"
    headers = {"Authorization": "Bearer sessionId"}


def get_mocked_metadata(*args, **kwargs):
    path = Path(__file__).resolve().parent / "sample_json" / "analytics_tabular_metadata"
    with open(path, "r") as f:
        return json.loads(f.read())


def get_json(json_file):
    path = Path(__file__).resolve().parent / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())


jsons = [get_json("analytics_tabular_initial"), get_json("analytics_tabular")]


class TestSalesforce(unittest.TestCase):
    @patch("reportforce.report.get_metadata", get_mocked_metadata)
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request):
        mocked_request().json.side_effect = jsons
        self.report = get_report(
            "report_id", id_column="Opportunity Name", session=FakeLogin
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


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
