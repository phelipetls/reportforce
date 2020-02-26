import os
import sys
import unittest

from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402
from utils import mocks  # noqa: E402


headers = {"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'}

mocked_response = Mock(headers=headers)
mocked_response.iter_content = lambda chunk_size: b"1,2,3\na,b,c"

metadata = mocks.get_json("analytics_tabular_metadata")


class TestExcelWithoutFilename(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):
        mocked_metadata.return_value = metadata

        mocked_request.return_value.__enter__.return_value = mocked_response

        self.m = mock_open()
        with patch("reportforce.report.open", self.m, create=True):
            self.excel = get_report("report_id", excel=True, session=mocks.FakeLogin)

    def test_get_excel_report(self):
        self.m.assert_called_once_with("spreadsheet.xlsx", "wb")


class TestExcelWithFileName(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch("reportforce.helpers.request_report.POST")
    def setUp(self, mocked_request, mocked_metadata):
        mocked_metadata.return_value = metadata

        mocked_request.return_value.__enter__.return_value = mocked_response

        self.m = mock_open()
        with patch("reportforce.report.open", self.m, create=True):
            self.excel = get_report(
                "report_id", excel="filename.xlsx", session=mocks.FakeLogin
            )

    def test_get_excel_report_specific_filename(self):
        self.m.assert_called_once_with("filename.xlsx", "wb")


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
