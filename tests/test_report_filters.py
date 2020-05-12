import pytest
import pandas as pd

from reportforce import Reportforce
from reportforce.helpers import report_filters

from fixtures_utils import read_json

REPORT = read_json("tabular.json")
METADATA = read_json("tabular_metadata.json")


@pytest.fixture
def setup(mock_login, mock_generate_reports, mock_get_metadata):
    """Simulate getting a report with these parameters.

    We expected the underlying report metadata dictionary
    to change accordingly.
    """
    mock_generate_reports(REPORT, n=2)
    mock_get_metadata(METADATA)

    rf = Reportforce("foo@bar.com", "1234", "XXX")
    rf.get_report(
        "ID",
        filters=[("Opportunity Name", "!=", "VALUE")],
        logic="1 AND 2",
        id_column="Opportunity Name",
        start="01-01-2020",
        end="2020-01-31",
        date_column="Fiscal Period",
    )

    return rf


def test_logic(setup):
    logic = setup.metadata.boolean_filter
    expected_logic = "1 AND 2 AND 3"

    assert logic == expected_logic


def test_date_filter(setup):
    dates = setup.metadata.std_date_filter
    expected_dates = {
        "column": "FISCAL_QUARTER",
        "durationValue": "CUSTOM",
        "startDate": "2020-01-01",
        "endDate": "2020-01-31",
    }

    assert dates == expected_dates


def test_report_filters(setup):
    filters = setup.metadata.report_filters
    expected_filters = [
        {
            "column": "column",
            "filterType": "filterType",
            "isRunPageEditable": True,
            "operator": "operator",
            "value": "value",
        },
        {"column": "OPPORTUNITY_NAME", "operator": "notEqual", "value": "VALUE"},
        {
            "column": "OPPORTUNITY_NAME",
            "operator": "notEqual",
            "value": "Acme - 200 Widgets,Acme - 200 Widgets",
        },
    ]

    assert filters == expected_filters


def test_sort_by(setup):
    report_filters.set_sort_by("Opportunity Name", "asc", METADATA)

    sort_by = METADATA["reportMetadata"]["sortBy"]

    assert sort_by["sortColumn"] == "OPPORTUNITY_NAME"
    assert sort_by["sortOrder"] == "Asc"


def test_sort_by_error(setup):
    with pytest.raises(ValueError) as err:
        report_filters.set_sort_by("Opportunity Name", "orientation", METADATA)

    assert str(err.value) == (
        "Orientation should be either 'asc' or 'desc', not 'orientation'"
    )


def test_tabular_by_sorting(
    mock_login, mock_generate_reports, mock_get_metadata, monkeypatch
):
    mock_get_metadata(read_json("tabular_metadata.json"))

    fact_map = REPORT["factMap"]["T!T"]
    rows = fact_map["rows"] * 2000

    new_rows = []

    for i, row in enumerate(rows):
        cell = row["dataCells"].copy()
        new_value = cell[6].copy()
        new_value["value"] = i
        cell[6] = new_value
        new_rows.append({"dataCells": cell})

    monkeypatch.setitem(fact_map, "rows", new_rows)
    mock_generate_reports(REPORT)

    rf = Reportforce("fake@username.com", "1234", "token")
    rf.get_report("ID", id_column="Age")

    assert rf.metadata.sort_by == {
        "sortColumn": "AGE",
        "sortOrder": "Asc",
    }

    assert rf.metadata.report_filters[-1] == {
        "column": "AGE",
        "operator": "greaterThan",
        "value": 1999,
    }
