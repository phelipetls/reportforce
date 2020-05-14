import pandas as pd

from reportforce.helpers.tabular import Tabular

from fixtures_utils import read_json

TABULAR_REPORT = read_json("tabular.json")
EXPECTED_TABULAR_DF = pd.read_pickle("tests/data/tabular_df.pickle")


def test_tabular_to_dataframe():
    """Test tabular report DataFrame converter."""
    tabular_df = Tabular(TABULAR_REPORT).to_dataframe()

    pd.testing.assert_frame_equal(EXPECTED_TABULAR_DF, tabular_df)


EMPTY_FACTMAP = {"T!T": {"rows": []}}


def test_empty_tabular(monkeypatch):
    """Test if DataFrame is empty when there are no rows in factMap."""
    monkeypatch.setitem(TABULAR_REPORT, "factMap", EMPTY_FACTMAP)

    assert Tabular(TABULAR_REPORT).to_dataframe().empty
