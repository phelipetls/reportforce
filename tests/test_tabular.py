import os
import sys
import unittest
import pandas as pd

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import Reportforce  # noqa: E402

df = pd.DataFrame(
    [
        [
            "Acme - 200 Widgets",
            16000.01,
            16000.01,
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
            16000.01,
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
    ],
)

report = mocks.get_json("analytics_tabular")


class TestTabularReport(unittest.TestCase):
    def setUp(self):
        mocks.mock_get_metadata("analytics_tabular_metadata").start()
        mocks.mock_login().start()

        self.rf = Reportforce("foo@bar.com", "1234", "XXX")

    @patch.object(Reportforce.session, "post")
    def test_dataframe(self, post):
        """Test if the generated DataFrame is what we expected, including dtypes."""
        post().json.side_effect = mocks.generate_reports(report)

        df = self.rf.get_report("report_id", id_column="Opportunity Name")

        expected_df = df
        pd.testing.assert_frame_equal(df, expected_df)

    @patch.object(Reportforce.session, "post")
    def test_empty_report(self, post):
        """Test if an empty DataFrame is returned in case of an empty report."""
        mock_factmap = {"T!T": {"aggregates": {"label": 0, "value": 0}, "rows": []}}

        with patch.dict(report, values=report, factMap=mock_factmap):
            post().json.return_value = report

            df = self.rf.get_report("report_id")

        self.assertTrue(df.empty)

    @patch.object(Reportforce.session, "get")
    def test_get_total(self, get):
        """Test getting the grand total of a report."""
        get().json.return_value = report

        test = self.rf.get_total("report_id")
        expected = 16000.01

        self.assertEqual(test, expected)

    def tearDown(self):
        patch.stopall()


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
