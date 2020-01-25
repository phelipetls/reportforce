import os
import sys
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.login import soap_login, AuthenticationError  # noqa: E402


def get_login(login_type):
    xml_path = Path(__file__).resolve().parent / "sample_xml" / login_type
    with open(xml_path, "r") as xml_file:
        return xml_file.read()


class TestSoapLogin(unittest.TestCase):
    @patch("requests.post")
    def test_successful_login(self, mockpost):
        mockpost.return_value = Mock(status_code=200, text=get_login("successful.xml"))

        test = soap_login("fake@username.com", "pass", "XXX")
        expected = ("sessionId", "dummy.salesforce.com")

        self.assertEqual(test, expected)

    @patch("requests.post")
    def test_failed_login(self, mockpost):
        mockpost.return_value = Mock(status_code=500, text=get_login("failed.xml"))

        with self.assertRaises(AuthenticationError):
            soap_login("fake@username.com", "pass", "XXX")


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
