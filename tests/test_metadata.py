import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_metadata  # noqa: E402
from utils import mocks  # noqa: E402


class TestGetMetadata(unittest.TestCase):

    url = "https://dummy.salesforce.com/services/data/v47.0/analytics/reports/ID/describe"
    headers = {"Authorization": "Bearer sessionId"}

    @patch("reportforce.report.request_report.GET")
    def test_request_call_to_get_metadata(self, mock_request):
        get_metadata("ID", session=mocks.FakeLogin)
        mock_request.assert_called_with(self.url, headers=self.headers)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
