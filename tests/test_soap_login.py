import pytest

from fixtures_utils import read_data
from reportforce.login import soap_login, AuthenticationError

SUCCESS = read_data("login_successful.xml")
FAILURE = read_data("login_failed.xml")

USERNAME = "fake@username.com"
PASSWORD = "pass"
TOKEN = "token"


class MockXmlResponse:
    def __init__(self, data, code, *args, **kwargs):
        self.text = data
        self.status_code = code


@pytest.fixture
def mock_success_login(mocker):
    """
    Do not make a POST request, return a XML response as if the login had
    succeded.
    """
    xml_response = MockXmlResponse(data=SUCCESS, code=200)

    return mocker.patch("requests.post", return_value=xml_response)


def test_xml_response_parser(mock_success_login):
    """
    Test if function correctly get session id and instance URL from the XML
    response body.
    """
    test = soap_login(USERNAME, PASSWORD, TOKEN)
    expected = ("sessionId", "www.salesforce.com")

    assert test == expected


EXPECTED_URL = "https://login.salesforce.com/services/Soap/u/47.0"

EXPECTED_HEADERS = {
    "Content-Type": "text/xml; charset=UTF-8",
    "SoapAction": "login",
}

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


def test_post_request_call(mock_success_login):
    """Test if POST request is called with expected parameters."""
    soap_login(USERNAME, PASSWORD, TOKEN)

    mock_success_login.assert_called_with(
        EXPECTED_URL,
        headers=EXPECTED_HEADERS,
        data=BODY_TEMPLATE.format(USERNAME, PASSWORD, TOKEN),
    )


def test_escape_xml_body(mock_success_login):
    """
    Test if POST request is called with expected parameters, when there are
    special XML characters in the credentials.
    """
    soap_login("<>&", "<>&", "<>&")

    mock_success_login.assert_called_with(
        EXPECTED_URL,
        headers=EXPECTED_HEADERS,
        data=BODY_TEMPLATE.format("&lt;&gt;&amp;", "&lt;&gt;&amp;", "&lt;&gt;&amp;"),
    )


def test_authentication_with_getpass(mock_success_login, mocker):
    mocker.patch("reportforce.login.input", return_value=USERNAME)
    mocker.patch("reportforce.login.getpass", side_effect=[PASSWORD, "token<>&"])

    soap_login()

    mock_success_login.assert_called_with(
        EXPECTED_URL,
        headers=EXPECTED_HEADERS,
        data=BODY_TEMPLATE.format(USERNAME, PASSWORD, "token&lt;&gt;&amp;"),
    )


@pytest.fixture
def mock_failed_login(mocker):
    """
    Do not make a POST request, return a XML response as if the login had
    failed.
    """
    xml_response = MockXmlResponse(data=FAILURE, code=500)

    return mocker.patch("requests.post", return_value=xml_response)


def test_failed_login(mock_failed_login):
    with pytest.raises(AuthenticationError) as err:
        soap_login(USERNAME, PASSWORD, TOKEN)

    expected = (
        "INVALID_LOGIN: Invalid username, password, "
        "security token; or user locked out."
    )

    assert str(err.value) == expected
