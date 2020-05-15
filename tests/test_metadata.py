from fixtures_utils import read_json
from reportforce.helpers.metadata import Metadata

metadata = Metadata(read_json("tabular_metadata.json"))


def test_get_column_info():
    assert metadata.get_columns_info() == {
        "Age": {"api_name": "AGE", "dtype": "int"},
        "Amount": {"api_name": "AMOUNT", "dtype": "currency"},
        "Created Date": {"api_name": "CREATED_DATE", "dtype": "datetime"},
        "Fiscal Period": {"api_name": "FISCAL_QUARTER", "dtype": "string"},
        "Lead Source": {"api_name": "LEAD_SOURCE", "dtype": "picklist"},
        "Next Step": {"api_name": "NEXT_STEP", "dtype": "string"},
        "Opportunity Name": {"api_name": "OPPORTUNITY_NAME", "dtype": "string"},
        "Opportunity Owner": {"api_name": "FULL_NAME", "dtype": "string"},
        "Owner Role": {"api_name": "ROLLUP_DESCRIPTION", "dtype": "string"},
        "Probability (%)": {"api_name": "PROBABILITY", "dtype": "percent"},
    }


def test_get_columns_labels():
    assert metadata.get_columns_labels() == [
        "Opportunity Name",
        "Amount",
        "Lead Source",
        "Next Step",
        "Probability (%)",
        "Fiscal Period",
        "Age",
        "Created Date",
        "Opportunity Owner",
        "Owner Role",
    ]


def test_get_columns_dtypes():
    assert metadata.get_columns_dtypes() == [
        "string",
        "currency",
        "picklist",
        "string",
        "percent",
        "string",
        "int",
        "datetime",
        "string",
        "string",
    ]


def test_get_column_api_name():
    assert metadata.get_column_api_name("Opportunity Name") == "OPPORTUNITY_NAME"


def test_get_column_dtype():
    assert metadata.get_column_dtype("Opportunity Name") == "string"


def test_get_operator():
    assert metadata.get_operator("==") == "equals"


def test_format_date():
    assert metadata.format_value("01-02-2020", "Created Date") == "2020-02-01T00:00:00"


def test_format_string():
    assert metadata.format_value("OpportunityName1", "Opportunity Name") == (
        '"OpportunityName1"'
    )


def test_format_multiple_strings():
    values = ["Name1", "Name2"]
    assert metadata.format_value(values, "Opportunity Name") == ('"Name1","Name2"')


def test_format_number():
    assert metadata.format_value(1, "Amount") == ('"1"')


def test_format_multiple_numbers():
    assert metadata.format_value([1, 2, 3], "Amount") == ('"1","2","3"')


def test_get_groupings_label():
    assert Metadata(read_json("summary_metadata.json")).get_groupings_labels() == [
        "label"
    ]
