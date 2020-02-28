import os
import sys
import unittest
import pandas as pd

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import Reportforce, get_report  # noqa: E402
from utils import mocks  # noqa: E402

metadata = mocks.get_json("analytics_tabular_metadata")
report = mocks.get_json("analytics_tabular")


class TestTabularReport(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.sf = Reportforce(mocks.FakeLogin)

    def test_get_docstring(self):
        self.assertEqual(self.sf.get.__doc__, get_report.__doc__)

    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def test_get_functionality(self, mocked_request, mocked_metadata):

        mocked_metadata.return_value = metadata
        mocked_request().json.return_value = report

        test = self.sf.get("000O1a0940aXYhz")
        self.assertIsInstance(test, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
