import pytest

from reportforce import Reportforce
from fixtures_utils import read_json


class ExcelResponse:
    headers = {"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'}

    def iter_content(*args, **kwargs):
        return b"1,2,3"

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(*args, **kwargs):
        pass


@pytest.fixture
def mock_post(mock_get_metadata, monkeypatch):
    mock_get_metadata(read_json("tabular_metadata.json"))

    def _mock_post_response(*args, **kwargs):
        return ExcelResponse()

    monkeypatch.setattr(Reportforce.session, "post", _mock_post_response)


@pytest.fixture
def mock_open(mocker):
    return mocker.patch("builtins.open", mocker.mock_open())


@pytest.mark.usefixtures("mock_login", "mock_post")
class TestExcel:
    """Test getting and writing report as a spreadsheet into the filesystem."""

    def test_download_excel_without_filename(self, mock_open):
        """If user do not provide a filename, use the one in the headers."""
        Reportforce("foo@bar.com", "1234", "token").get_report("ID", excel=True)

        mock_open.assert_called_with("spreadsheet.xlsx", "wb")

    def test_download_excel_with_filename(self, mock_open):
        """If user provides a filename, use it to save the spreadsheet."""
        Reportforce("foo@bar.com", "1234", "token").get_report("ID", excel="file.xlsx")

        mock_open.assert_called_with("file.xlsx", "wb")
