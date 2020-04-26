import pytest

from reportforce.login import Salesforce
from fixtures_utils import read_json, MockJsonResponse

USERNAME = "fake@username.com"
PASSWORD = "pass"
TOKEN = "token"


def test_soap_login(mock_login):
    """Test authentication via user-password-token method."""
    sf = Salesforce(USERNAME, PASSWORD, TOKEN)

    assert sf.version == "47.0"
    assert sf.session_id == "sessionId"
    assert sf.instance_url == "www.salesforce.com"
    assert sf.headers == {"Authorization": "Bearer sessionId"}


def test_use_session_id(mock_login):
    """Test authentication when user provides session ID and instance URL directly."""
    sf = Salesforce(session_id="userSessionId", instance_url="www.enterprise.com")

    assert sf.version == "47.0"
    assert sf.session_id == "userSessionId"
    assert sf.instance_url == "www.enterprise.com"
    assert sf.headers == {"Authorization": "Bearer userSessionId"}


VERSIONS = read_json("versions.json")


@pytest.fixture
def mock_get_request(monkeypatch):
    def _mock_get_request(*args, **kwargs):
        return MockJsonResponse(VERSIONS)

    monkeypatch.setattr("requests.get", _mock_get_request)


def test_get_latest_version(mock_login, mock_get_request):
    """Test getting latest version of Salesforce."""
    sf = Salesforce(USERNAME, PASSWORD, TOKEN, latest_version=True)

    assert sf.version == "48.0"
