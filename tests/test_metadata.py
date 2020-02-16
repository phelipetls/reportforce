import os
import sys
import json
import unittest

from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_metadata  # noqa: E402


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


class TestSalesforce(unittest.TestCase):

    url = "https://dummy.salesforce.com/services/data/v47.0/analytics/reports/ID/describe"
    headers = {"Authorization": "Bearer sessionId"}

    @patch("reportforce.report.request_report.GET")
    def test_request_call_to_get_metadata(self, mockrequest):
        get_metadata("ID", session=FakeLogin)
        mockrequest.assert_called_with(self.url, headers=self.headers)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
