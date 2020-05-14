import pytest

from fixtures_utils import read_data
from reportforce import login

SUCCESS = read_data("login_successful.xml")
FAILURE = read_data("login_failed.xml")

USERNAME = "fake@username.com"
PASSWORD = "pass"
TOKEN = "token"


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

    assert login.soap_login(USERNAME, PASSWORD, TOKEN) == (
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
    login.generate_soap_body(USERNAME, PASSWORD, TOKEN) == BODY_TEMPLATE.format(
        "username", "password", "token"
    )


def test_generate_soap_body_escaped():
    login.generate_soap_body(
        "&lt;&gt;&amp;", "&lt;&gt;&amp;", "&lt;&gt;&amp;"
    ) == BODY_TEMPLATE.format("<>&", "<>&", "<>&")


def test_generate_soap_body_with_stdin(mocker):
    mocker.patch("reportforce.login.input", return_value=USERNAME)
    mocker.patch("reportforce.login.getpass", side_effect=[PASSWORD, "token<>&"])

    login.generate_soap_body(USERNAME, PASSWORD, TOKEN) == BODY_TEMPLATE.format(
        USERNAME, PASSWORD, TOKEN
    )


def test_failed_login(requests_mock):
    requests_mock.post(
        "https://login.salesforce.com/services/Soap/u/47.0",
        text=FAILURE,
        status_code=500,
    )

    with pytest.raises(login.AuthenticationError) as err:
        login.soap_login(USERNAME, PASSWORD, TOKEN)

    expected = (
        "INVALID_LOGIN: Invalid username, password, "
        "security token; or user locked out."
    )

    assert str(err.value) == expected
