import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import report, Reportforce  # noqa: E402

URL = "https://dummy.salesforce.com/services/data/v47.0/analytics/reports/report_id/describe"

soap_login_config = {"return_value": ("sessionId", "dummy.salesforce.com")}


class TestGetMetadata(unittest.TestCase):
    def setUp(self):
        soap_login = patch("reportforce.login.soap_login", **soap_login_config)
        soap_login.start()

    @patch.object(Reportforce.session, "get")
    def test_request_call_to_get_metadata(self, get):
        rf = Reportforce("foo@bar.com", "1234", "XXX")
        rf.get_report("report_id")

        get.assert_called_with(URL)

    def tearDown(self):
        patch.stopall()


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
