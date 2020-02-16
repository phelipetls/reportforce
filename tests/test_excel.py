import os
import sys
import json
import unittest

from pathlib import Path
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402


class FakeLogin:
    """Fake Salesforce session object"""

    version = "47.0"
    session_id = "sessionId"
    instance_url = "dummy.salesforce.com"
    headers = {"Authorization": "Bearer sessionId"}


def get_json(json_file):
    path = Path(__file__).resolve().parent / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())


headers = {"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'}


class TestSalesforce(unittest.TestCase):
    @patch("reportforce.helpers.request_report.GET")
    def setUp(self, mocked_request):
        mocked_request.return_value = Mock(headers=headers, content=b"1,2,3\na,b,c")

        self.m = mock_open()
        with patch("reportforce.report.open", self.m, create=True):
            self.excel = get_report("report_id", excel=True, session=FakeLogin)

    def test_get_excel_report(self):
        self.m.assert_called_once_with("spreadsheet.xlsx", "wb")


class Test(unittest.TestCase):
    @patch("reportforce.helpers.request_report.GET")
    def setUp(self, mocked_request):
        mocked_request.return_value = Mock(headers=headers, content=b"1,2,3\na,b,c")

        self.m = mock_open()
        with patch("reportforce.report.open", self.m, create=True):
            self.excel = get_report("report_id", excel="filename.xlsx", session=FakeLogin)

    def test_get_excel_report_specific_filename(self):
        self.m.assert_called_once_with("filename.xlsx", "wb")


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
