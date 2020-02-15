import os
import sys
import json
import unittest

from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import set_filters, set_period, set_logic  # noqa: E402


def get_mocked_metadata(*args, **kwargs):
    path = Path(__file__).resolve().parent / "sample_json" / "analytics_tabular_metadata"
    with open(path, "r") as f:
        return json.loads(f.read())


class TestSalesforce(unittest.TestCase):

    maxdiff = None

    filters = [("Opportunity Name", "!=", "VALUE")]
    period = ("01-01-2020", "2020-01-31")
    logic = "1 AND 2"

    def setUp(self):
        self.metadata = get_mocked_metadata()

        set_filters(self.filters, self.metadata)

        start, end = self.period
        date_column = "Fiscal Period"
        set_period(start, end, date_column, self.metadata)

        set_logic(self.logic, self.metadata)

    def test_logic(self):
        test = self.metadata["reportBooleanFilter"]
        expected = "1 AND 2"
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
    unittest.main()

# vi: nowrap
