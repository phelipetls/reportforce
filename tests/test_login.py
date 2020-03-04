import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.login import Salesforce  # noqa: E402


class TestSalesforce(unittest.TestCase):
    """Test Salesforce class main properties."""

    @patch("reportforce.login.soap_login")
    def test_salesforce_class(self, mock_soap_login):

        mock_soap_login.return_value = ("sessionId", "dummy.salesforce.com")
        sf = Salesforce("foo@bar.com", "pass", "XXX")

        self.assertEqual(sf.version, "47.0")
        self.assertEqual(sf.session_id, "sessionId")
        self.assertEqual(sf.instance_url, "dummy.salesforce.com")
        self.assertEqual(sf.headers, {"Authorization": "Bearer sessionId"})


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
