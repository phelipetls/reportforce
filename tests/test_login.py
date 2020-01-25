import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.login import Login  # noqa: E402


class TestLogin(unittest.TestCase):
    @patch("reportforce.login.soap_login")
    def setUp(self, mock_soap_login):
        mock_soap_login.return_value = ("sessionId", "dummy.salesforce.com")
        self.sf = Login("foo@bar.com", "pass", "XXX")

    def test_salesforce_class(self):
        self.assertEqual(self.sf.version, "47.0")
        self.assertEqual(self.sf.session_id, "sessionId")
        self.assertEqual(self.sf.instance_url, "dummy.salesforce.com")
        self.assertEqual(self.sf.headers, {"Authorization": "Bearer sessionId"})


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
