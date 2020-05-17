import pytest

from reportforce import Reportforce
from reportforce.helpers.metadata import Metadata

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
    Test if the filter was incremented one times due
    to filtering out already seen values.
    """
    assert len(setup.metadata.report_filters) == 3
    assert setup.metadata.boolean_filter == "1 AND 2 AND 3"


def test_date_filter(setup):
    """
    Test if date filter has the user-specified values.
    """
    assert setup.metadata.date_filter == {
        "column": "FISCAL_QUARTER",
        "durationValue": "CUSTOM",
        "startDate": "2020-01-01T00:00:00",
        "endDate": "2020-01-31T00:00:00",
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
        {"column": "OPPORTUNITY_NAME", "operator": "notEqual", "value": '"00112233"'},
        {
            "column": "OPPORTUNITY_NAME",
            "operator": "notEqual",
            "value": '"Acme - 200 Widgets"',
        },
    ]


def test_ignore_date_filter(mock_login, mock_get_metadata, mock_http_request):
    """Test if specifying ignore_date_filter removes the standard date filter."""
    mock_get_metadata(METADATA)
    mock_http_request(REPORT, "post")

    rf = Reportforce("foo@bar.com", "1234", "token")
    rf.get_report("ID", ignore_date_filter=True)

    assert rf.metadata.date_filter == {
        "column": "column",
        "durationValue": "CUSTOM",
        "endDate": None,
        "startDate": None,
    }


def test_set_date_interval(mock_login, mock_get_metadata, mock_http_request):
    """Test if specifying a date interval gives the correct date filter."""
    mock_get_metadata(Metadata(read_json("sample_metadata.json")))
    mock_http_request(REPORT, "post")

    rf = Reportforce("foo@bar.com", "1234", "token")
    rf.get_report("ID", date_interval="Current FY")

    assert rf.metadata.date_filter == {
        "column": "CLOSE_DATE",
        "durationValue": "THIS_FISCAL_YEAR",
        "endDate": "2016-12-31T00:00:00",
        "startDate": "2016-01-01T00:00:00",
    }
