import os
import sys
import json
import unittest
import requests

from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402
from reportforce.helpers.request import ReportError  # noqa: E402


class FakeLogin:
    """Fake Salesforce session object"""

    version = "47.0"
    session_id = "sessionId"
    instance_url = "dummy.salesforce.com"
    headers = {"Authorization": "Bearer sessionId"}


def get_mocked_metadata(*args, **kwargs):
    path = Path(__file__).resolve().parent / "sample_json" / "analytics_metadata"
    with open(path, "r") as f:
        return json.loads(f.read())


def get_json(json_file):
    path = Path(__file__).resolve().parent / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())


class TestSalesforce(unittest.TestCase):
    @patch("reportforce.report.get_metadata", get_mocked_metadata)
    @patch.object(requests.Session, "post")
    def test_if_raises(self, mocked_session):
        mocked_session().json.return_value = get_json("analytics_error")
        with self.assertRaises(ReportError):
            get_report("report_id", session=FakeLogin)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
