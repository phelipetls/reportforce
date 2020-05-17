import pytest

from fixtures_utils import read_data
from reportforce import login

SUCCESS = read_data("login_successful.xml")
FAILURE = read_data("login_failed.xml")

EXPECTED_URL = "https://login.salesforce.com/services/Soap/u/47.0"

EXPECTED_HEADERS = {
    "Content-Type": "text/xml; charset=UTF-8",
    "SoapAction": "login",
}


def test_xml_response_parser(requests_mock, mocker):
    """Test readin session ID and instance URL from XML response."""
    requests_mock.post(
        "https://login.salesforce.com/services/Soap/u/47.0", text=SUCCESS
    )

    assert login.soap_login("foo@bar.com", "pass", "token") == (
        "sessionId",
        "www.salesforce.com",
    )


BODY_TEMPLATE = """<?xml version="1.0" encoding="utf-8" ?>
    <env:Envelope
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <env:Body>
            <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                <n1:username>{}</n1:username>
                <n1:password>{}{}</n1:password>
            </n1:login>
        </env:Body>
    </env:Envelope>"""


def test_generate_soap_body():
    assert login.generate_soap_body("foo@bar.com", "pass", "token") == BODY_TEMPLATE.format(
        "foo@bar.com", "pass", "token"
    )


def test_generate_soap_body_escaped():
    assert login.generate_soap_body("<>&", "<>&", "<>&") == BODY_TEMPLATE.format(
        "&lt;&gt;&amp;", "&lt;&gt;&amp;", "&lt;&gt;&amp;"
    )


def test_generate_soap_body_with_stdin(mocker):
    mocker.patch("builtins.input", return_value="foo@bar.com")
    mocker.patch("reportforce.login.getpass", side_effect=["pass", "token<>&"])

    assert login.generate_soap_body("foo@bar.com", "pass", "token<>&") == BODY_TEMPLATE.format(
        "foo@bar.com", "pass", "token&lt;&gt;&amp;"
    )


def test_failed_login(requests_mock):
    requests_mock.post(
        "https://login.salesforce.com/services/Soap/u/47.0",
        text=FAILURE,
        status_code=500,
    )

    with pytest.raises(login.AuthenticationError) as err:
        login.soap_login("foo@bar.com", "pass", "token")

    expected = (
        "INVALID_LOGIN: Invalid username, password, "
        "security token; or user locked out."
    )

    assert str(err.value) == expected
