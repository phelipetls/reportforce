import unittest

from utils import mocks
from unittest.mock import patch
from reportforce import Reportforce
from reportforce.login import Salesforce, AuthenticationError


class TestSalesforce(unittest.TestCase):
    """Test Salesforce class main properties."""

    @patch("reportforce.login.soap_login")
    def test_soap_login(self, soap_login):
        """Test authentication via user-password-token method."""
        soap_login.return_value = ("sessionId", "dummy.salesforce.com")

        sf = Salesforce("foo@bar.com", "pass", "XXX")

        self.assertEqual(sf.version, "47.0")
        self.assertEqual(sf.session_id, "sessionId")
        self.assertEqual(sf.instance_url, "dummy.salesforce.com")
        self.assertEqual(sf.headers, {"Authorization": "Bearer sessionId"})

    def test_use_session_id(self):
        """Test authentication when user provides session ID and instance directly."""
        session_id, instance_url = ("userSessionId", "dummy.salesforce.com")

        sf = Salesforce(session_id=session_id, instance_url=instance_url)

        self.assertEqual(sf.version, "47.0")
        self.assertEqual(sf.session_id, "userSessionId")
        self.assertEqual(sf.instance_url, "dummy.salesforce.com")
        self.assertEqual(sf.headers, {"Authorization": "Bearer userSessionId"})

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
