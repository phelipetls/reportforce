from fixtures_utils import read_json
from reportforce.helpers.metadata import Metadata

metadata = Metadata(read_json("sample_metadata.json"))


class TestGetters:
    def test_get_column_api_name(self):
        assert metadata.get_column_api_name("Opportunity Name") == "OPPORTUNITY_NAME"

    def test_get_column_label(self):
        assert metadata.get_column_label("OPPORTUNITY_NAME") == "Opportunity Name"

    def test_get_column_dtype(self):
        assert metadata.get_column_dtype("OPPORTUNITY_NAME") == "string"

    def test_get_columns_labels(self):
        assert metadata.get_columns_labels() == [
            "Owner Role",
            "Opportunity Owner",
            "Account Name",
            "Opportunity Name",
            "Stage",
            "Fiscal Period",
            "Amount",
            "Probability (%)",
            "Age",
            "Close Date",
            "Created Date",
            "Next Step",
            "Lead Source",
            "Type",
        ]

    def test_get_columns_dtypes(self):
        assert metadata.get_columns_dtypes() == [
            "string",
            "string",
            "string",
            "string",
            "picklist",
            "string",
            "currency",
            "percent",
            "int",
            "date",
            "datetime",
            "string",
            "picklist",
            "picklist",
        ]

    def test_get_operator(self):
        assert metadata.get_operator("==") == "equals"

    def test_get_aggregate_api_name(self):
        assert metadata.get_column_api_name("Record Count") == "RowCount"

    def test_get_aggregate_label(self):
        assert metadata.get_column_label("RowCount") == "Record Count"

    def test_get_aggregate_dtype(self):
        assert metadata.get_column_dtype("RowCount") == "int"

    def test_get_non_included_column_api_name(self):
        assert (
            metadata.get_column_api_name("Last Modified Alias")
            == "LAST_UPDATE_BY_ALIAS"
        )

    def test_get_non_included_column_label(self):
        assert (
            metadata.get_column_label("LAST_UPDATE_BY_ALIAS") == "Last Modified Alias"
        )

    def test_get_non_included_column_dtype(self):
        assert metadata.get_column_dtype("LAST_UPDATE_BY_ALIAS") == "string"

    def test_get_groupings_label(self):
        assert metadata.get_groupings_labels() == [
            "Close Date",
            "Stage",
            "Account Name",
            "Account: Last Activity",
        ]

    def test_get_date_filter_duration_groups(self):
        assert metadata.get_date_filter_durations_groups() == {
            "Current FY": {
                "end": "2016-12-31",
                "start": "2016-01-01",
                "value": "THIS_FISCAL_YEAR",
            },
            "Custom": {"end": "2016-12-12", "start": "2016-12-13", "value": "CUSTOM"},
            "Previous FY": {
                "end": "2015-12-31",
                "start": "2015-01-01",
                "value": "LAST_FISCAL_YEAR",
            },
        }


class TestFormatValue:
    def test_format_date(self):
        assert (
            metadata.format_value("01-02-2020", "CREATED_DATE") == "2020-02-01T00:00:00"
        )

    def test_format_multiple_dates(self):
        assert (
            metadata.format_value(["01-02-2020", "02-02-2020"], "CREATED_DATE")
            == "2020-02-01T00:00:00,2020-02-02T00:00:00"
        )

    def test_format_string(self):
        assert metadata.format_value("Name", "OPPORTUNITY_NAME") == '"Name"'

    def test_format_multiple_strings(self):
        assert metadata.format_value(["Name", "Another"], "OPPORTUNITY_NAME") == (
            '"Name","Another"'
        )

    def test_format_number(self):
        assert metadata.format_value(1, "AMOUNT") == ('"1"')

    def test_format_multiple_numbers(self):
        assert metadata.format_value([1, 2, 3], "AMOUNT") == ('"1","2","3"')


class TestIncrementBooleanFilter:
    def test_simple_filter(self):
        test = "1 AND 2 AND 3"
        expected = "1 AND 2 AND 3 AND 4"
        assert Metadata._add_new_filter_to_boolean_filter(test) == expected

    def test_difficult_filter(self):
        test = "(((1 AND 2) AND 3) AND 4)"
        expected = "(((1 AND 2) AND 3) AND 4) AND 5"
        assert Metadata._add_new_filter_to_boolean_filter(test) == expected
