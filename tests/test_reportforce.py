import os
import sys
import unittest
import pandas as pd

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import report, Reportforce  # noqa: E402

mock_metadata = mocks.get_json("analytics_tabular_metadata")
mock_report = mocks.get_json("analytics_tabular")

URL = (
    "https://dummy.salesforce.com/services/data/v47.0/analytics/reports/000O1a0940aXYhz"
)


@patch.object(Reportforce.session, "post")
class TestTabularReport(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        mocks.mock_get_metadata("analytics_tabular_metadata").start()
        mocks.mock_login().start()

        self.rf = Reportforce("foo@bar.com", "1234", "XXX")

    def test_get_report_call_with_no_params(self, post):
        """With no params, we expect the params parameter in the call."""
        post().json.return_value = mock_report
        self.rf.get_report("000O1a0940aXYhz")

        post.assert_called_with(
            URL, json=mock_metadata, params={"includeDetails": "true"},
        )

    def test_get_report_call_with_params(self, post):
        """With params, we expect them to be merged into the default."""
        post().json.return_value = mock_report
        self.rf.get_report("000O1a0940aXYhz", params={"another": "param"})

        post.assert_called_with(
            URL,
            json=mock_metadata,
            params={"includeDetails": "true", "another": "param"},
        )


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
