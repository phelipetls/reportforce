import os
import sys
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.login import soap_login, AuthenticationError  # noqa: E402


expected_url = "https://login.salesforce.com/services/Soap/u/47.0"

expected_headers = {
    "Content-Type": "text/xml; charset=UTF-8",
    "SoapAction": "login",
}

expected_body = """<?xml version="1.0" encoding="utf-8" ?>
    <env:Envelope
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <env:Body>
            <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                <n1:username>fake@username.com</n1:username>
                <n1:password>passXXX</n1:password>
            </n1:login>
        </env:Body>
    </env:Envelope>"""


def get_login(login_type):
    xml_path = Path(__file__).resolve().parent / "sample_xml" / login_type
    with open(xml_path, "r") as xml_file:
        return xml_file.read()


class TestSoapLogin(unittest.TestCase):
    @patch("requests.post")
    def test_successful_login(self, post):
        post.return_value = Mock(status_code=200, text=get_login("successful.xml"))

        test = soap_login("fake@username.com", "pass", "XXX")
        expected = ("sessionId", "dummy.salesforce.com")

        self.assertEqual(test, expected)

        post.assert_called_with(
            expected_url, headers=expected_headers, data=expected_body
        )

    @patch("requests.post")
    def test_failed_login(self, post):
        post.return_value = Mock(status_code=500, text=get_login("failed.xml"))

        with self.assertRaises(AuthenticationError):
            soap_login("fake@username.com", "pass", "XXX")


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
