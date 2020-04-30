import pytest
import pandas as pd

from fixtures_utils import read_json

from reportforce.helpers import parsers

REPORT = read_json("tabular.json")
METADATA = read_json("tabular_metadata.json")


def test_get_value():
    """Test getting values of different data types of a 'cell' in a factMap."""

    currency_cell = cell={"label": "$29", "value": 29}
    assert parsers.get_value(currency_cell, dtype="currency") == 29

    currency_cell = {"label": "$29", "value": {"amount": 29, "currency": None}}
    assert parsers.get_value(currency_cell, "currency") == 29

    date_cell = {"label": "7/31/2015", "value": "2015-07-31"}
    assert parsers.get_value(date_cell, "date") == pd.Timestamp("2015-07-31")

    others = {"label": "Qualitative", "value": "QUALITATIVE"}
    assert parsers.get_value(others, "picklist") == "Qualitative"


def test_map_columns_to_dtypes():
    """If not a matrix, we expect the information on detailColumnInfo."""
    columns_to_dtypes = parsers.map_columns_to_dtypes(METADATA)

    assert columns_to_dtypes == {
        "Age": "int",
        "Amount": "currency",
        "Created Date": "datetime",
        "Fiscal Period": "string",
        "Lead Source": "picklist",
        "Next Step": "string",
        "Opportunity Name": "string",
        "Opportunity Owner": "string",
        "Owner Role": "string",
        "Probability (%)": "percent",
    }


def test_map_columns_to_dtypes_matrix(monkeypatch):
    """If it's a matrix, we expect the information on aggregateColumnInfo."""
    monkeypatch.setitem(METADATA["reportMetadata"], "reportFormat", "MATRIX")

    assert parsers.map_columns_to_dtypes(METADATA) == {"label": "dataType"}


def test_get_columns_dtypes():
    dtypes = parsers.get_columns_dtypes(METADATA)
    assert list(dtypes) == [
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


def test_get_column_dtype():
    assert parsers.get_column_dtype("Age", METADATA) == "int"


def test_get_columns_labels():
    columns_labels = parsers.get_columns_labels(METADATA)
    assert columns_labels == {
        "Age": "AGE",
        "Amount": "AMOUNT",
        "Created Date": "CREATED_DATE",
        "Fiscal Period": "FISCAL_QUARTER",
        "Lead Source": "LEAD_SOURCE",
        "Next Step": "NEXT_STEP",
        "Opportunity Name": "OPPORTUNITY_NAME",
        "Opportunity Owner": "FULL_NAME",
        "Owner Role": "ROLLUP_DESCRIPTION",
        "Probability (%)": "PROBABILITY",
    }
