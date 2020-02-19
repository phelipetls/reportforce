import os
import sys
import json
import unittest

from pathlib import Path
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402
from utils import mocks


headers = {"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'}


class TestExcelWithoutFilename(unittest.TestCase):
    @patch("reportforce.helpers.request_report.GET")
    def setUp(self, mocked_request):
        mocked_request.return_value = Mock(headers=headers, content=b"1,2,3\na,b,c")

        self.m = mock_open()
        with patch("reportforce.report.open", self.m, create=True):
            self.excel = get_report("report_id", excel=True, session=mocks.FakeLogin)

    def test_get_excel_report(self):
        self.m.assert_called_once_with("spreadsheet.xlsx", "wb")


class TestExcelWithFileName(unittest.TestCase):
    @patch("reportforce.helpers.request_report.GET")
    def setUp(self, mocked_request):
        mocked_request.return_value = Mock(headers=headers, content=b"1,2,3\na,b,c")

        self.m = mock_open()
        with patch("reportforce.report.open", self.m, create=True):
            self.excel = get_report("report_id", excel="filename.xlsx", session=mocks.FakeLogin)

    def test_get_excel_report_specific_filename(self):
        self.m.assert_called_once_with("filename.xlsx", "wb")


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
