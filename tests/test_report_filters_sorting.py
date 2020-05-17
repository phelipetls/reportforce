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
        "ID", id_column="Opportunity Owner",
    )

    return rf


def test_report_filters(setup):
    assert setup.metadata.report_filters == [
        {
            "column": "column",
            "filterType": "filterType",
            "isRunPageEditable": True,
            "operator": "operator",
            "value": "value",
        },
        {
            "column": "FULL_NAME",
            "operator": "greaterThan",
            "value": '"Fred Wiliamson"',
        },
    ]


def test_sort_by(setup):
    assert setup.metadata.sort_by == [{"sortColumn": "FULL_NAME", "sortOrder": "Asc"}]
