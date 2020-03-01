import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce import Reportforce  # noqa: E402
from reportforce.report import get_metadata  # noqa: E402
from utils import mocks  # noqa: E402


class TestGetMetadata(unittest.TestCase):

    url = (
        "https://dummy.salesforce.com/services/data/v47.0/analytics/reports/ID/describe"
    )
    headers = {"Authorization": "Bearer sessionId"}

    @patch.object(Reportforce.session, "get")
    def test_request_call_to_get_metadata(self, mock_request):
        sf = Reportforce(mocks.FakeLogin)
        get_metadata("ID", salesforce=sf)

        self.assertIn("Authorization", sf.session.headers)
        mock_request.assert_called_with(self.url)

def test_request_call_to_get_metadata(self, mock_request):
    sf = Reportforce(mocks.FakeLogin)
    get_metadata("ID", salesforce=sf)

    assert sf.session.headers["Authorization"] == "Bearer sessionId"

if __name__ == "__main__":
    unittest.main()

# vi: nowrap
