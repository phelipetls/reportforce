from reportforce.helpers.report import Report
from reportforce.helpers.matrix import Matrix

from fixtures_utils import read_json

tabular = Report(read_json("tabular.json"))


class TestReportFunctions:
    def test_report_columns_dtypes(self):
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

    def test_report_columns_labels(self):
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

    def test_report_get_columns_dtype(self):
        assert tabular.get_column_dtype("Opportunity Name") == "string"


matrix = Matrix(read_json("matrix.json"))


class TestMatrix:
    def test_get_matrix_columns_labels(self):
        assert matrix.get_matrix_columns().tolist() == [
            ("Row Sum", "Product", "DeliveryDay1"),
            ("Row Sum", "Product", "DeliveryDay2"),
            ("Row Sum", "Product", "DeliveryDay3"),
            ("Row Sum", "Product", "DeliveryDay4"),
        ]

    def test_get_groupings_down_labels(self):
        assert matrix.get_groupings_labels(matrix.report_metadata["groupingsDown"]) == [
            "Supervisor",
            "Worker",
        ]

    def test_get_groupings_across_labels(self):
        assert matrix.get_groupings_labels(
            matrix.report_metadata["groupingsAcross"]
        ) == ["Product", "Delivery Day",]
