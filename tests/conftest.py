import pytest
import reportforce

from reportforce import Reportforce
from fixtures_utils import MockJsonResponse


@pytest.fixture
def mock_http_request(monkeypatch):
    """
    Do not make a HTTP request via Reportforce.session,
    return a local file instead.
    """

    def _mock_http_request(data, method):
        response = MockJsonResponse(data)

        monkeypatch.setattr(
            Reportforce.session, method, lambda *args, **kwargs: response
        )

    return _mock_http_request


@pytest.fixture
def mock_generate_reports(mocker):
    """
    Simulate receiving the same report via a POST request twice, the first one
    with the allData attribute set to False, and the last one with it set to
    True.
    """

    def _mock_generate_reports(data, n=1, **kwargs):
        all_data_false = data.copy()
        all_data_false["allData"] = False

        generator = map(MockJsonResponse, [all_data_false] * n + [data])

        mocker.patch.object(
            Reportforce.session, "post", side_effect=generator
        )

    return _mock_generate_reports


@pytest.fixture
def mock_login(monkeypatch):
    """Simulate logging into Salesforce."""

    def mock_soap_login(*args, **kwargs):
        return ("sessionId", "www.salesforce.com")

    monkeypatch.setattr(reportforce.login, "soap_login", mock_soap_login)


@pytest.fixture
def mock_get_metadata(monkeypatch):
    """Simulate getting a report metadata."""

    def _mock_get_metadata(metadata, *args, **kwargs):
        monkeypatch.setattr(
            reportforce.Reportforce, "get_metadata", lambda *args, **kwargs: metadata,
        )

    return _mock_get_metadata
