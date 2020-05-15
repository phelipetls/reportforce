from reportforce.helpers.report import Report
from fixtures_utils import read_json

tabular = Report(read_json("tabular.json"))


def test_map_columns_to_info():
    assert tabular.map_columns_to_info() == {
        "Age": {"api_name": "AGE", "dtype": "int"},
        "Amount": {"api_name": "AMOUNT", "dtype": "currency"},
        "Created Date": {"api_name": "CREATED_DATE", "dtype": "datetime"},
        "Fiscal Period": {"api_name": "FISCAL_QUARTER", "dtype": "string"},
        "Lead Source": {"api_name": "LEAD_SOURCE", "dtype": "currency"},
        "Next Step": {"api_name": "NEXT_STEP", "dtype": "string"},
        "Opportunity Name": {"api_name": "OPPORTUNITY_NAME", "dtype": "string"},
        "Opportunity Owner": {"api_name": "FULL_NAME", "dtype": "string"},
        "Owner Role": {"api_name": "ROLLUP_DESCRIPTION", "dtype": "string"},
        "Probability (%)": {"api_name": "PROBABILITY", "dtype": "percent"},
    }


def test_report_columns_dtypes():
    assert tabular.get_columns_dtypes() == [
        "string",
        "currency",
        "currency",
        "string",
        "percent",
        "string",
        "int",
        "datetime",
        "string",
        "string",
    ]


def test_report_columns_labels():
    assert tabular.get_columns_labels() == [
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


def test_report_get_columns_dtype():
    assert tabular.get_column_dtype("Opportunity Name") == "string"


matrix = Report(read_json("matrix.json"))


def test_get_matrix_columns_labels():
    assert matrix.get_columns_labels().tolist() == [
        ("Row Sum", "Product", "DeliveryDay1"),
        ("Row Sum", "Product", "DeliveryDay2"),
        ("Row Sum", "Product", "DeliveryDay3"),
        ("Row Sum", "Product", "DeliveryDay4"),
    ]


def test_get_groupings_down_labels():
    assert matrix.get_groupings_labels(matrix.report_metadata["groupingsDown"]) == [
        "Supervisor",
        "Worker",
    ]


def test_get_groupings_across_labels():
    assert matrix.get_groupings_labels(matrix.report_metadata["groupingsAcross"]) == [
        "Product",
        "Delivery Day",
    ]
