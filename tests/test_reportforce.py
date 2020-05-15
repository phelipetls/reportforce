from reportforce import Reportforce
from reportforce.helpers.metadata import Metadata

from fixtures_utils import read_json


def test_get_report_url(mock_login):
    rf = Reportforce("fake@username.com", "pass", "token")
    assert rf._get_report_url("ID") == (
        "https://www.salesforce.com/services/data/v47.0/analytics/reports/ID"
    )


METADATA_URL = (
    "https://www.salesforce.com/services/data/v47.0/analytics/reports/ID/describe"
)


def test_get_metadata_url(mock_login):
    rf = Reportforce("fake@username.com", "pass", "token")
    assert rf._get_metadata_url("ID") == (METADATA_URL)


def test_get_metadata(mock_login, requests_mock):
    requests_mock.get(METADATA_URL, json=read_json("tabular_metadata.json"))

    metadata = Reportforce("fake@username.com", "pass", "token").get_metadata("ID")
    assert isinstance(metadata, Metadata)
