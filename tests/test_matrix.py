import pytest
import pandas as pd

from reportforce import Reportforce
from reportforce.helpers.parsers import get_columns_labels

from fixtures_utils import read_json

MATRIX_REPORT = read_json("matrix.json")
MATRIX_METADATA = read_json("matrix_metadata.json")


@pytest.fixture
def setup(mock_login, mock_http_request, mock_get_metadata):
    mock_http_request(MATRIX_REPORT, "post")
    mock_get_metadata(MATRIX_METADATA)


expected_matrix_df = pd.read_pickle("tests/data/expected_matrix.pickle")


def test_matrix_to_dataframe(setup):
    """Test matrix report into DataFrame converter."""
    rf = Reportforce("foo@bar.com", "1234", "XXX")
    matrix_df = rf.get_report("ID")

    pd.testing.assert_frame_equal(expected_matrix_df, matrix_df)


EMPTY_FACTMAP = {"T!T": {"rows": []}}


def test_empty_matrix(setup, monkeypatch):
    """Test if returns an empty DataFrame when the matrix is empty."""
    monkeypatch.setitem(MATRIX_REPORT, "factMap", EMPTY_FACTMAP)

    rf = Reportforce("foo@bar.com", "1234", "XXX")
    matrix_df = rf.get_report("ID")

    assert matrix_df.empty


def test_get_columns_labels():
    """Test reportforce.helpers.parsers.get_columns_labels function."""
    columns_labels = get_columns_labels(MATRIX_REPORT)

    expected_columns_labels = {
        "Delivery Day": "Delivery Day",
        "Product": "Product",
        "Supervisor": "Supervisor",
        "Worker": "Worker",
    }

    assert columns_labels == expected_columns_labels
