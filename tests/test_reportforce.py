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


class TestTabularReport(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.sf = Reportforce(mocks.FakeLogin)

    @patch("reportforce.report.get_metadata")
    @patch.object(Reportforce.session, "post")
    def test_get_functionality(self, post, get_metadata):
        """Simulate getting a JSON and check if it turns into a DataFrame."""

        get_metadata.return_value = mock_metadata
        post().json.return_value = mock_report

        test = self.sf.get("000O1a0940aXYhz")
        self.assertIsInstance(test, pd.DataFrame)

    def test_get_docstring(self):
        self.assertEqual(self.sf.get.__doc__, report.get_report.__doc__)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
