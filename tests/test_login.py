import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce import Reportforce  # noqa: E402
from reportforce.login import Salesforce, AuthenticationError  # noqa: E402
from utils import mocks  # noqa: E402


class TestSalesforce(unittest.TestCase):
    """Test Salesforce class main properties."""

    @patch("reportforce.login.soap_login")
    def test_salesforce_soap_login(self, soap_login):
        """Test authentication via user-password-token method."""

        soap_login.return_value = ("sessionId", "dummy.salesforce.com")
        sf = Salesforce("foo@bar.com", "pass", "XXX")

        self.assertEqual(sf.version, "47.0")
        self.assertEqual(sf.session_id, "sessionId")
        self.assertEqual(sf.instance_url, "dummy.salesforce.com")
        self.assertEqual(sf.headers, {"Authorization": "Bearer sessionId"})

    def test_salesforce_use_session_id(self):
        """Test authentication when user provides session ID and instance directly."""
        session_id, instance_url = ("sessionId", "dummy.salesforce.com")
        sf = Salesforce(session_id=session_id, instance_url=instance_url)

        self.assertEqual(sf.version, "47.0")
        self.assertEqual(sf.session_id, "sessionId")
        self.assertEqual(sf.instance_url, "dummy.salesforce.com")
        self.assertEqual(sf.headers, {"Authorization": "Bearer sessionId"})


    def test_salesforce_authentication_error(self):
        """Test if raises Authentication Error when no valid arguments are passed."""
        with self.assertRaises(AuthenticationError):
            Salesforce()

        with self.assertRaises(AuthenticationError):
            Salesforce(session_id="session_id", password="pass")

        with self.assertRaises(AuthenticationError):
            Salesforce(username="username", password="pass")

    def test_get_latest_version(self):
        """Test getting latest version of Salesforce."""
        get_config = {"get.return_value.json.return_value": mocks.get_json("versions")}

        with patch("reportforce.login.requests", **get_config):
            rf = Reportforce(
                session_id="session_id", instance_url="instance", latest_version=True
            )
            test = rf.version
            expected = "48.0"

        self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
