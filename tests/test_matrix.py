import os
import sys
import unittest
import pandas as pd

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import Reportforce  # noqa: E402

mock_metadata = mocks.get_json("analytics_matrix_metadata")
mock_report = mocks.get_json("analytics_matrix")


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
    ],
    names=["Supervisor", "Worker"],
)

columns = pd.MultiIndex.from_tuples(
    [
        ("Row Sum", "Product", "DeliveryDay1"),
        ("Row Sum", "Product", "DeliveryDay2"),
        ("Row Sum", "Product", "DeliveryDay3"),
        ("Row Sum", "Product", "DeliveryDay4"),
    ],
    names=["", "Product", "Delivery Day"],
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


metadata_config = {"return_value": mock_metadata}
soap_login_config = {"return_value": ("sessionId", "dummy.salesforce.com")}


class TestMatrixReport(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        soap_login = patch("reportforce.login.soap_login", **soap_login_config)
        get_metadata = patch("reportforce.report.get_metadata", **metadata_config)

        soap_login.start()
        get_metadata.start()

        self.rf = Reportforce("foo@bar.com", "1234", "XXX")

    @patch.object(Reportforce.session, "post")
    def test_dataframe(self, post):
        post().json.return_value = mock_report

        df = self.rf.get_report("ReportID")
        pd.testing.assert_frame_equal(expected_df, df)

    @patch.object(Reportforce.session, "post")
    def test_empty_matrix(self, post):
        mock_factmap = {
            "T!T": {"aggregates": {"label": "label", "value": "value"}, "rows": []}
        }

        with patch.dict(mock_report, mock_report, factMap=mock_factmap):
            post().json.return_value = mock_report
            df = self.rf.get_report("ReportID")

            self.assertTrue(df.empty)

    def tearDown(self):
        patch.stopall()


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
