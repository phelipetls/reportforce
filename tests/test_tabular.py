import pytest
import pandas as pd

from reportforce import Reportforce
from fixtures_utils import read_json

TABULAR_REPORT = read_json("tabular.json")
TABULAR_METADATA = read_json("tabular_metadata.json")


@pytest.fixture
def setup(mock_login, mock_http_request, mock_get_metadata):
    mock_get_metadata(TABULAR_METADATA)
    mock_http_request(TABULAR_REPORT, "post")


expected_tabular_df = pd.read_pickle("tests/data/tabular_df.pickle")


def test_tabular_to_dataframe(setup, mock_generate_reports):
    """Test tabular report DataFrame converter."""
    mock_generate_reports(TABULAR_REPORT)

    rf = Reportforce("fake@username.com", "1234", "token")
    tabular_df = rf.get_report("ID", id_column="Opportunity Name")

    pd.testing.assert_frame_equal(expected_tabular_df, tabular_df)


EMPTY_FACTMAP = {"T!T": {"rows": []}}


def test_empty_tabular(setup, monkeypatch):
    """Test if DataFrame is empty when there are no rows in factMap."""
    monkeypatch.setitem(TABULAR_REPORT, "factMap", EMPTY_FACTMAP)

    rf = Reportforce("fake@username.com", "1234", "token")
    tabular_df = rf.get_report("ID", id_column="Opportunity Name")

    assert tabular_df.empty
