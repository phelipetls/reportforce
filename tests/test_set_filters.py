import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import mocks  # noqa: E402
from reportforce.helpers import filtering  # noqa: E402


class TestFiltersSetters(unittest.TestCase):

    maxdiff = None

    filters = [("Opportunity Name", "!=", "VALUE")]
    period = ("01-01-2020", "2020-01-31")
    logic = "1 AND 2"

    @classmethod
    def setUpClass(cls):
        cls.metadata = mocks.get_json("analytics_tabular_metadata")

        filtering.set_filters(cls.filters, cls.metadata)

        start, end = cls.period
        date_column = "Fiscal Period"
        filtering.set_period(start, end, date_column, cls.metadata)

        filtering.set_logic(cls.logic, cls.metadata)

        filtering.increment_logical_filter(cls.metadata)

    def test_logic(self):
        test = self.metadata["reportMetadata"]["reportBooleanFilter"]
        expected = "1 AND 2 AND 3"
        self.assertEqual(test, expected)

    def test_date_filter(self):
        test = self.metadata["reportMetadata"]["standardDateFilter"]
        expected = {
            "column": "FISCAL_QUARTER",
            "durationValue": "CUSTOM",
            "startDate": "2020-01-01",
            "endDate": "2020-01-31",
        }
        self.assertDictEqual(test, expected)

    def test_report_filters(self):
        test = self.metadata["reportMetadata"]["reportFilters"]
        expected = [
            {
                "column": "column",
                "filterType": "filterType",
                "isRunPageEditable": True,
                "operator": "operator",
                "value": "value",
            },
            {"column": "OPPORTUNITY_NAME", "operator": "notEqual", "value": "VALUE"},
        ]
        self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
