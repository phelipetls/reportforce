from reportforce.helpers.report import Report
from fixtures_utils import read_json

tabular = Report(read_json("tabular.json"))


def test_report_dtypes():
    assert tabular.get_dtypes() == [
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


def test_report_columns():
    assert tabular.get_columns() == [
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


def test_get_matrix_columns():
    assert matrix.get_columns().tolist() == [
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
