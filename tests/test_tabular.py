import os
import sys
import unittest
import pandas as pd

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402
from utils import mocks  # noqa: E402

metadata = mocks.get_json("analytics_tabular_metadata")
report = mocks.get_json("analytics_tabular")

df = pd.DataFrame(
    [
        [
            "Acme - 200 Widgets",
            16000.01,
            "Word of mouth",
            "Need estimate",
            0.6,
            "Q3-2015",
            12,
            "2015-07-31",
            "Fred Wiliamson",
            "-",
        ],
        [
            "Acme - 200 Widgets",
            16000.01,
            "Word of mouth",
            "Need estimate",
            0.6,
            "Q3-2015",
            12,
            "2015-07-31",
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
).astype(
    {
        "Opportunity Name": "string",
        "Amount": "float64",
        "Lead Source": "string",
        "Next Step": "string",
        "Probability (%)": "float64",
        "Fiscal Period": "string",
        "Age": "int",
        "Created Date": "datetime64",
        "Opportunity Owner": "string",
        "Owner Role": "string",
    }
)


class TestTabularReport(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):

        mocked_report = report
        mocked_metadata.return_value = metadata

        with patch.dict(mocked_report, values=mocked_report, allData=False, clear=True):
            mocked_request().json.side_effect = [mocked_report] * 2

            self.report = get_report(
                "report_id", id_column="Opportunity Name", session=mocks.FakeLogin
            )

    def test_dataframe(self):
        test = self.report
        expected = df
        pd.testing.assert_frame_equal(test, expected)


class TestEmptyTabular(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):

        mocked_metadata.return_value = metadata

        mocked_factmap = {"T!T": {"aggregates": {"label": 0, "value": 0}, "rows": []}}

        with patch.dict(report, values=report, factMap=mocked_factmap):
            mocked_request().json.return_value = report

            self.report = get_report(
                "report_id", id_column="Opportunity Name", session=mocks.FakeLogin
            )

    def test_empty_report(self):
        self.assertTrue(self.report.empty)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
