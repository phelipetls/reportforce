import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import report, Reportforce  # noqa: E402

URL = "https://dummy.salesforce.com/services/data/v47.0/analytics/reports/ID/describe"


class TestGetMetadata(unittest.TestCase):

    @patch.object(Reportforce.session, "get")
    def test_request_call_to_get_metadata(self, get):
        rf = Reportforce(mocks.FakeLogin)
        report.get_metadata("ID", salesforce=rf)

        self.assertIn("Authorization", rf.session.headers)
        get.assert_called_with(URL)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
