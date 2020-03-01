import os
import sys
import unittest
import pandas as pd

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce import Reportforce  # noqa: E402
from utils import mocks  # noqa: E402

metadata = mocks.get_json("analytics_matrix_metadata")
report = mocks.get_json("analytics_matrix")


class TestMatrixReport(unittest.TestCase):
    maxDiff = None

    @patch("reportforce.report.get_metadata")
    @patch.object(Reportforce.session, "post")
    def test_dataframe(self, mocked_report, mocked_metadata):

        mocked_metadata.return_value = metadata
        mocked_report().json.return_value = report

        indices = pd.MultiIndex.from_tuples(
            [
                ("Supervisor1", "Worker1"),
                ("Supervisor1", "Worker2"),
                ("Supervisor2", "Worker3"),
                ("Supervisor2", "Worker4"),
                ("Supervisor2", "Worker5"),
                ("Supervisor2", "Worker6"),
                ("Supervisor2", "Worker7"),
                ("Supervisor2", "Worker8"),
                ("Supervisor3", "Worker9"),
                ("Supervisor4", "Worker10"),
                ("Supervisor4", "Worker11"),
                ("Supervisor4", "Worker12"),
            ], names=["Supervisor", "Worker"]
        )
        columns = pd.MultiIndex.from_tuples(
            [
                ("Row Sum", "Product", "DeliveryDay1"),
                ("Row Sum", "Product", "DeliveryDay2"),
                ("Row Sum", "Product", "DeliveryDay3"),
                ("Row Sum", "Product", "DeliveryDay4"),
            ], names=["", "Product", "Delivery Day"]
        )
        expected_df = pd.DataFrame(
            [
                ["0_0!0_0", "0_0!0_1", "0_0!0_2", "0_0!0_3"],
                ["0_1!0_0", "0_1!0_1", "0_1!0_2", "0_1!0_3"],
                ["1_0!0_0", "1_0!0_1", "1_0!0_2", "1_0!0_3"],
                ["1_1!0_0", "1_1!0_1", "1_1!0_2", "1_1!0_3"],
                ["1_2!0_0", "1_2!0_1", "1_2!0_2", "1_2!0_3"],
                ["1_3!0_0", "1_3!0_1", "1_3!0_2", "1_3!0_3"],
                ["1_4!0_0", "1_4!0_1", "1_4!0_2", "1_4!0_3"],
                ["1_5!0_0", "1_5!0_1", "1_5!0_2", "1_5!0_3"],
                ["2_0!0_0", "2_0!0_1", "2_0!0_2", "2_0!0_3"],
                ["3_0!0_0", "3_0!0_1", "3_0!0_2", "3_0!0_3"],
                ["3_1!0_0", "3_1!0_1", "3_1!0_2", "3_1!0_3"],
                ["3_2!0_0", "3_2!0_1", "3_2!0_2", "3_2!0_3"],
            ],
            index=indices,
            columns=columns,
        )

        sf = Reportforce(mocks.FakeLogin)
        df = sf.get("ReportID")

        pd.testing.assert_frame_equal(expected_df, df, check_dtype=False)

    @patch("reportforce.report.get_metadata")
    @patch.object(Reportforce.session, "post")
    def test_empty_matrix(self, mocked_request, mocked_metadata):

            mocked_metadata.return_value = metadata
            mocked_report = report

            mocked_factmap = {
                "T!T": {"aggregates": {"label": "label", "value": "value"}, "rows": []}
            }

            with patch.dict(mocked_report, mocked_report, factMap=mocked_factmap):
                mocked_request().json.return_value = mocked_report

                sf = Reportforce(mocks.FakeLogin)
                df = sf.get("ReportID")
                self.assertTrue(df.empty)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
