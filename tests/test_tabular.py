import os
import sys
import unittest
import pandas as pd

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import Reportforce  # noqa: E402

mock_metadata = mocks.get_json("analytics_tabular_metadata")
mock_report = mocks.get_json("analytics_tabular")

df = pd.DataFrame(
    [
        [
            "Acme - 200 Widgets",
            16000.01,
            "Word of mouth",
            "Need estimate",
            60,
            "Q3-2015",
            12,
            pd.Timestamp("2015-07-31"),
            "Fred Wiliamson",
            "-",
        ],
        [
            "Acme - 200 Widgets",
            16000.01,
            "Word of mouth",
            "Need estimate",
            60,
            "Q3-2015",
            12,
            pd.Timestamp("2015-07-31"),
            "Fred Wiliamson",
            "-",
        ],
    ],
    columns=[
        "Opportunity Name",
        "Amount",
        "Lead Source",
        "Next Step",
        "Probability (%)",
        "Fiscal Period",
        "Age",
        "Created Date",
        "Opportunity Owner",
        "Owner Role",
    ]
)


class TestTabularReport(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch.object(Reportforce.session, "post")
    def setUp(self, post, get_metadata):

        get_metadata.return_value = mock_metadata

        with patch.dict(mock_report, values=mock_report, allData=False, clear=True):
            post().json.side_effect = [mock_report] * 2

            sf = Reportforce(mocks.FakeLogin)
            self.report = sf.get("report_id", id_column="Opportunity Name")

    def test_dataframe(self):
        test = self.report
        expected = df
        pd.testing.assert_frame_equal(test, expected)


class TestEmptyTabular(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch.object(Reportforce.session, "post")
    def setUp(self, post, get_metadata):

        get_metadata.return_value = mock_metadata

        mock_factmap = {"T!T": {"aggregates": {"label": 0, "value": 0}, "rows": []}}

        with patch.dict(mock_report, values=mock_report, factMap=mock_factmap):
            post().json.return_value = mock_report

            sf = Reportforce(mocks.FakeLogin)
            self.report = sf.get("report_id", id_column="Opportunity Name")

    def test_empty_report(self):
        self.assertTrue(self.report.empty)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
