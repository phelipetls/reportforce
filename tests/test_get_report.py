import pytest

from reportforce import Reportforce

EXPECTED_URL = "https://www.salesforce.com/services/data/v47.0/analytics/reports/ID"

METADATA = {"reportMetadata": {"reportFormat": "TABULAR"}}


@pytest.fixture
def setup(mock_login, mock_get_metadata):
    mock_get_metadata(METADATA)


@pytest.fixture
def mock_post(mocker):
    return mocker.patch.object(Reportforce.session, "post")


def test_get_report_no_kwargs(setup, mock_post):
    """Without kwargs, we expect params={'includeDetaisl': 'true'} in the POST request call."""
    rf = Reportforce("fake@username.com", "1234", "XXX")
    rf.get_report("ID")

    mock_post.assert_called_with(
        EXPECTED_URL, json=METADATA, params={"includeDetails": "true"}
    )


def test_get_report_with_kwargs(setup, mock_post):
    """Test if kwargs provided by user overwrite defaults."""
    rf = Reportforce("fake@username.com", "1234", "XXX")
    rf.get_report("ID", timeout=30, params={"includeDetails": "false"})

    mock_post.assert_called_with(
        EXPECTED_URL, json=METADATA, timeout=30, params={"includeDetails": "false"}
    )


def test_get_report_without_params_in_kwargs(setup, mock_post):
    """Test if includeDetails enters the call even if user did not pass it."""
    rf = Reportforce("fake@username.com", "1234", "XXX")
    rf.get_report("ID", timeout=30)

    mock_post.assert_called_with(
        EXPECTED_URL, json=METADATA, timeout=30, params={"includeDetails": "true"}
    )
