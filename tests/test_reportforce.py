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


@patch("reportforce.report.get_metadata")
@patch.object(Reportforce.session, "post")
class TestTabularReport(unittest.TestCase):
    maxDiff = None

    @patch("reportforce.login.soap_login")
    def setUp(self, soap_login):
        soap_login.return_value = ("sessionId", "dummy.salesforce.com")

        self.rf = Reportforce("foo@bar.com", "1234", "XXX")

    def test_get_report_call_with_params(self, post, get_metadata):
        """Assure that includeDetails is passed into post request."""

        get_metadata.return_value = mock_metadata
        post().json.return_value = mock_report

        self.rf.get_report("000O1a0940aXYhz")

        post.assert_called_with(
            URL, json=mock_metadata, params={"includeDetails": "true"},
        )

    def test_get_report_call_no_params(self, post, get_metadata):
        """Assure that user-defined parameter in passed alongside includeDetails."""

        get_metadata.return_value = mock_metadata
        post().json.return_value = mock_report

        self.rf.get_report("000O1a0940aXYhz", params={"another": "param"})

        post.assert_called_with(
            URL,
            json=mock_metadata,
            params={"includeDetails": "true", "another": "param"},
        )

    def test_if_result_is_dataframe(self, post, get_metadata):
        """Simulate getting a JSON and check if it turns into a DataFrame."""

        get_metadata.return_value = mock_metadata
        post().json.return_value = mock_report

        test = self.rf.get_report("000O1a0940aXYhz", params={"another": "param"})

        self.assertIsInstance(test, pd.DataFrame)


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
