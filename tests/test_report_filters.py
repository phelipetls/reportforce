import pytest

from reportforce import Reportforce

from fixtures_utils import read_json

REPORT = read_json("tabular.json")
METADATA = read_json("tabular_metadata.json")


@pytest.fixture
def setup(mock_login, mock_generate_reports, mock_get_metadata):
    """
    Simulate looping 1 more time to get the full report.
    """
    mock_generate_reports(REPORT, n=1)
    mock_get_metadata(METADATA)

    rf = Reportforce("foo@bar.com", "1234", "token")
    rf.get_report(
        "ID",
        filters=[("Opportunity Name", "!=", "00112233")],
        logic="1 AND 2",
        id_column="Opportunity Name",
        start="01-01-2020",
        end="2020-01-31",
        date_column="Fiscal Period",
    )

    return rf


def test_logic(setup):
    """
    Test if the filter was incremented three times due
    1. to user-specified filter and
    2. to filtering out already seen values.
    """
    assert setup.metadata.boolean_filter == "1 AND 2 AND 3"


def test_date_filter(setup):
    """
    Test if date filter has the user-specified values.
    """
    assert setup.metadata.date_filter == {
        "column": "FISCAL_QUARTER",
        "durationValue": "CUSTOM",
        "startDate": "2020-01-01",
        "endDate": "2020-01-31",
    }


def test_report_filters(setup):
    """
    Test if a filter was added due
    1. to user-specified filter
    2. to filtering out already seen values.
    """
    assert setup.metadata.report_filters == [
        {
            "column": "column",
            "filterType": "filterType",
            "isRunPageEditable": True,
            "operator": "operator",
            "value": "value",
        },
        {"column": "OPPORTUNITY_NAME", "operator": "notEqual", "value": "00112233"},
        {
            "column": "OPPORTUNITY_NAME",
            "operator": "notEqual",
            "value": "Acme - 200 Widgets",
        }
    ]
