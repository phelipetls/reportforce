import unittest

from utils import mocks
from unittest.mock import patch
from reportforce import Reportforce

mock_metadata = mocks.get_json("analytics_tabular_metadata")
mock_report = mocks.get_json("analytics_tabular")

URL = (
    "https://dummy.salesforce.com/services/data"
    "/v47.0/analytics/reports/000O1a0940aXYhz"
)


@patch.object(Reportforce.session, "post")
class TestTabularReport(unittest.TestCase):
    """Test tabular report parser."""

    maxDiff = None

    def setUp(self):
        mocks.mock_login().start()
        mocks.mock_get_metadata("analytics_tabular_metadata").start()

        self.rf = Reportforce("foo@bar.com", "1234", "XXX")

    def test_get_report_call_with_no_additional_parameters(self, post):
        """Test post request with no additional parameters specified by user."""
        post().json.return_value = mock_report

        self.rf.get_report("000O1a0940aXYhz")

        post.assert_called_with(
            URL, json=mock_metadata, params={"includeDetails": "true"},
        )

    def test_get_report_call_with_additional_parameters(self, post):
        """Additional parameters should be merged with the defaults."""
        post().json.return_value = mock_report

        self.rf.get_report("000O1a0940aXYhz", params={"another": "param"})

        post.assert_called_with(
            URL,
            json=mock_metadata,
            params={"includeDetails": "true", "another": "param"},
        )

    def tearDown(self):
        patch.stopall()


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
