import pandas as pd

from reportforce.helpers.summary import Summary

from fixtures_utils import read_json

SUMMARY_REPORT = read_json("summary.json")
EXPECTED_SUMMARY_DF = pd.read_pickle("tests/data/summary_df.pickle")


def test_summary_to_dataframe():
    """Test summary report into DataFrame converter."""
    summary_df = Summary(SUMMARY_REPORT).to_dataframe()

    pd.testing.assert_frame_equal(EXPECTED_SUMMARY_DF, summary_df)


EMPTY_FACTMAP = {"T!T": {"rows": []}}


def test_empty_summary(monkeypatch):
    monkeypatch.setitem(SUMMARY_REPORT, "factMap", EMPTY_FACTMAP)

    assert Summary(SUMMARY_REPORT).to_dataframe().empty
