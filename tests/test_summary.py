import pytest
import pandas as pd

from reportforce import Reportforce

from fixtures_utils import read_json

SUMMARY_REPORT = read_json("summary.json")
SUMMARY_METADATA = read_json("summary_metadata.json")


@pytest.fixture
def setup(mock_login, mock_http_request, mock_get_metadata):
    mock_get_metadata(SUMMARY_METADATA)
    mock_http_request(SUMMARY_REPORT, "post")


expected_summary_df = pd.read_pickle("tests/data/summary_df.pickle")


def test_summary_to_dataframe(setup, mock_generate_reports):
    """Test summary report into DataFrame converter."""
    mock_generate_reports(SUMMARY_REPORT)

    rf = Reportforce("fake@username.com", "1234", "token")
    summary_df = rf.get_report("ID", id_column="label1")

    summary_df.to_pickle("tests/data/summary_df.pickle")

    pd.testing.assert_frame_equal(expected_summary_df, summary_df)


EMPTY_FACTMAP = {"T!T": {"rows": []}}


def test_empty_summary(setup, monkeypatch):
    monkeypatch.setitem(SUMMARY_REPORT, "factMap", EMPTY_FACTMAP)

    rf = Reportforce("fake@username.com", "1234", "token")
    summary_df = rf.get_report("ID", id_column="label1")

    assert summary_df.empty
