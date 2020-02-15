import os
import sys
import json
import unittest
import itertools

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
    path = (
        Path(__file__).resolve().parent / "sample_json" / "analytics_summary_metadata"
    )
    with open(path, "r") as f:
        return json.loads(f.read())


def get_json(json_file):
    path = Path(__file__).resolve().parent / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())

jsons = [get_json("analytics_summary_initial"), get_json("analytics_summary")]

class TestSalesforce(unittest.TestCase):
    @patch("reportforce.report.get_metadata", get_mocked_metadata)
    @patch("reportforce.helpers.request.request_report")
    def setUp(self, mocked_request):
        mocked_request.side_effect = jsons
        self.report = get_report("report_id", id_column="label1", session=FakeLogin)

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


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
