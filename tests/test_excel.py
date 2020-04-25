import unittest

from utils import mocks
from reportforce import Reportforce
from unittest.mock import patch, mock_open

mock_open = mock_open()
mock_metadata = mocks.get_json("analytics_tabular_metadata")


class ExcelResponse:
    headers = {"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'}

    def iter_content(chunk_size):
        return b"1,2,3\na,b,c"


post_config = {"return_value.__enter__.return_value": ExcelResponse}


class TestExcel(unittest.TestCase):
    """Test getting an Excel response and writing it to the filesystem."""

    def setUp(self):
        mocks.mock_login().start()
        mocks.mock_get_metadata("analytics_tabular_metadata").start()

        POST = patch.object(Reportforce.session, "post", **post_config)
        POST.start()

        self.rf = Reportforce("foo@bar.com", "1234", "XXX")

    def test_get_excel_without_filename(self):
        """When no filename is given, the one in the headers is used."""

        with patch("reportforce.report.open", mock_open, create=True):
            self.rf.get_report("report_id", excel=True)

        mock_open.assert_called_with("spreadsheet.xlsx", "wb")

    def test_get_excel_with_filename(self):
        """When a filename is given, this filename is used."""

        with patch("reportforce.report.open", mock_open, create=True):
            self.rf.get_report("report_id", excel="filename.xlsx")

        mock_open.assert_called_with("filename.xlsx", "wb")

    def tearDown(self):
        patch.stopall()


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
