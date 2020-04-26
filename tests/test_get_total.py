import pytest

from reportforce import Reportforce
from fixtures_utils import read_json, MockJsonResponse

EXPECTED_URL = "https://www.salesforce.com/services/data/v47.0/analytics/reports/ID"

METADATA = {"reportMetadata": {"reportFormat": "TABULAR"}}

REPORT = read_json("tabular.json")
FACTMAP = {"T!T": {"aggregates": [{"label": "$30", "value": 30}]}}


@pytest.fixture
def mock_get(mocker, monkeypatch):
    monkeypatch.setitem(REPORT, "factMap", FACTMAP)
    response = MockJsonResponse(REPORT)

    return mocker.patch.object(Reportforce.session, "get", return_value=response)


@pytest.fixture
def setup(mock_login, mock_get_metadata):
    mock_get_metadata(METADATA)


def test_get_total_call(setup, mock_get):
    rf = Reportforce("fake@username.com", "pass", "token")
    total = rf.get_total("ID")

    assert total == 30

    mock_get.assert_called_once_with(EXPECTED_URL, params={"includeDetails": "false"})
