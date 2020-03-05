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
    ],
)

mock_metadata = mocks.get_json("analytics_tabular_metadata")
mock_report = mocks.get_json("analytics_tabular")

metadata_config = {"return_value": mock_metadata}
soap_login_config = {"return_value": ("sessionId", "dummy.salesforce.com")}


class TestTabularReport(unittest.TestCase):
    def setUp(self):
        soap_login = patch("reportforce.login.soap_login", **soap_login_config)
        get_metadata = patch("reportforce.report.get_metadata", **metadata_config)

        soap_login.start()
        get_metadata.start()

        self.rf = Reportforce("foo@bar.com", "1234", "XXX")

    @patch.object(Reportforce.session, "post")
    def test_dataframe(self, post):
        with patch.dict(mock_report, values=mock_report, allData=False, clear=True):
            post().json.side_effect = [mock_report] * 2

            df = self.rf.get_report("report_id", id_column="Opportunity Name")

        expected_df = df
        pd.testing.assert_frame_equal(df, expected_df)

    @patch.object(Reportforce.session, "post")
    def test_empty_report(self, post):
        mock_factmap = {"T!T": {"aggregates": {"label": 0, "value": 0}, "rows": []}}

        with patch.dict(mock_report, values=mock_report, factMap=mock_factmap):
            post().json.return_value = mock_report

            df = self.rf.get_report("report_id")

        self.assertTrue(df.empty)

    @patch.object(Reportforce.session, "get")
    def test_get_total(self, get):
        get().json.return_value = mock_report

        test = self.rf.get_total("report_id")
        expected = 16000.01

        self.assertEqual(test, expected)

    def tearDown(self):
        patch.stopall()


# class TestGettingTotal(unittest.TestCase):
#     @patch("reportforce.report.get_metadata")
#     @patch.object(Reportforce.session, "get")
#     def test_get_total(self, get, get_metadata):

#         get_metadata.return_value = mock_metadata
#         get().json.return_value = mock_report

#         rf = Reportforce("foo@bar.com", "1234", "XXX")

#         test = rf.get_total("report_id")
#         expected = 16000.01

#         self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
