import os
import sys
import unittest

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce import Reportforce  # noqa: E402
from reportforce.helpers import sf_filters  # noqa: E402

mock_report = mocks.get_json("analytics_tabular")

class TestFiltersSetters(unittest.TestCase):

    maxdiff = None

    @classmethod
    @patch.object(Reportforce.session, "post")
    def setUpClass(cls, post):
        mocks.mock_login().start()
        mocks.mock_get_metadata("analytics_tabular_metadata").start()

        post().json.return_value = mock_report

        cls.rf = Reportforce("foo@bar.com", "1234", "XXX")

        cls.rf.get_report(
            "00O1a0000093ga",
            filters=[("Opportunity Name", "!=", "VALUE")],
            logic="1 AND 2",
            id_column="Opportunity Name",
            start="01-01-2020",
            end="2020-01-31",
            date_column="Fiscal Period"
        )

    def test_logic(self):
        test = self.rf.metadata["reportMetadata"]["reportBooleanFilter"]
        expected = "1 AND 2 AND 3"
        self.assertEqual(test, expected)

    def test_date_filter(self):
        test = self.rf.metadata["reportMetadata"]["standardDateFilter"]
        expected = {
            "column": "FISCAL_QUARTER",
            "durationValue": "CUSTOM",
            "startDate": "2020-01-01",
            "endDate": "2020-01-31",
        }
        self.assertDictEqual(test, expected)

    def test_report_filters(self):
        test = self.rf.metadata["reportMetadata"]["reportFilters"]
        expected = [
            {
                "column": "column",
                "filterType": "filterType",
                "isRunPageEditable": True,
                "operator": "operator",
                "value": "value",
            },
            {"column": "OPPORTUNITY_NAME", "operator": "notEqual", "value": "VALUE"},
            {"column": "OPPORTUNITY_NAME", "operator": "notEqual", "value": "Acme - 200 Widgets"},
        ]
        self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
