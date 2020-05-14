import pytest
import pandas as pd

from reportforce.helpers.matrix import Matrix

from fixtures_utils import read_json

MATRIX_REPORT = read_json("matrix.json")
EXPECTED_MATRIX_DF = pd.read_pickle("tests/data/expected_matrix.pickle")


def test_matrix_to_dataframe():
    """Test matrix report into DataFrame converter."""
    matrix_df = Matrix(MATRIX_REPORT).to_dataframe()

    pd.testing.assert_frame_equal(EXPECTED_MATRIX_DF, matrix_df)


EMPTY_FACTMAP = {"T!T": {"rows": []}}


def test_empty_matrix(monkeypatch):
    """Test if returns an empty DataFrame when the matrix is empty."""
    monkeypatch.setitem(MATRIX_REPORT, "factMap", EMPTY_FACTMAP)

    assert Matrix(MATRIX_REPORT).to_dataframe().empty
