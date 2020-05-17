from reportforce.login import Salesforce
from fixtures_utils import read_json

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


def test_change_version(mock_login):
    """Test authentication when user changes default version."""
    sf = Salesforce(USERNAME, PASSWORD, TOKEN, version="48.0")
    assert sf.version == "48.0"


VERSIONS = read_json("versions.json")


def test_get_latest_version(mock_login, requests_mock):
    """Test getting latest version of Salesforce."""
    requests_mock.get("https://www.salesforce.com/services/data/", json=VERSIONS)

    sf = Salesforce(USERNAME, PASSWORD, TOKEN, version="36.0", latest_version=True)
    assert sf.version == "48.0"
