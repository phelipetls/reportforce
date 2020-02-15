import os
import sys
import json
import unittest
import pandas as pd

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import reportforce # noqa: E402


class FakeLogin:
    """Fake Salesforce session object"""

    version = "47.0"
    session_id = "sessionId"
    instance_url = "dummy.salesforce.com"
    headers = {"Authorization": "Bearer sessionId"}


def get_json(json_file):
    path = Path(__file__).resolve().parent / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())

mocked_metadata = Mock(return_value = get_json("analytics_metadata_matrix"))

mocked_report = Mock(return_value = get_json("analytics_matrix"))

class TestMatrixReport(unittest.TestCase):
    maxDiff = None

    @patch("reportforce.report.get_metadata", mocked_metadata)
    @patch("reportforce.report.request.request_report", mocked_report)
    def test_dataframe(self):
        indices = pd.MultiIndex.from_tuples([
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
        ])
        columns = pd.MultiIndex.from_tuples([
            ("Product", "DeliveryDay1"),
            ("Product", "DeliveryDay2"),
            ("Product", "DeliveryDay3"),
            ("Product", "DeliveryDay4"),
        ])
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
        df = reportforce.report.get_report("ReportID", session=FakeLogin)
        pd.testing.assert_frame_equal(expected_df, df)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
