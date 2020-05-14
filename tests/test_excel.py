import pytest

from reportforce import Reportforce
from fixtures_utils import read_json


@pytest.fixture
def mock_request_excel(mock_get_metadata, requests_mock):
    mock_get_metadata(read_json("tabular_metadata.json"))

    requests_mock.post(
        "https://www.salesforce.com/services/data/v47.0/analytics/reports/ID",
        content=b"1,2,3",
        headers={"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'},
    )


@pytest.fixture
def mock_open(mocker):
    return mocker.patch("builtins.open", mocker.mock_open())


def test_download_excel_without_filename(mock_login, mock_request_excel, mock_open):
    Reportforce("foo@bar.com", "1234", "token").get_report("ID", excel=True)

    mock_open.assert_called_with("spreadsheet.xlsx", "wb")


def test_download_excel_with_filename(mock_login, mock_request_excel, mock_open):
    Reportforce("foo@bar.com", "1234", "token").get_report("ID", excel="file.xlsx")

    mock_open.assert_called_with("file.xlsx", "wb")


def test_excel_headers(mock_login):
    rf = Reportforce("foo@bar.com", "1234", "token")

    assert rf._get_excel_headers() == {
        "User-Agent": "python-requests/2.23.0",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Connection": "keep-alive",
        "Authorization": "Bearer sessionId",
    }
