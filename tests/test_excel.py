import os
import sys
import unittest

from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce import Reportforce
from reportforce.report import get_report  # noqa: E402
from utils import mocks  # noqa: E402


headers = {"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'}

mocked_response = Mock(headers=headers)
mocked_response.iter_content = lambda chunk_size: b"1,2,3\na,b,c"

metadata = mocks.get_json("analytics_tabular_metadata")


class TestExcelWithoutFilename(unittest.TestCase):

    @patch("reportforce.report.get_metadata")
    @patch.object(Reportforce.session, "post")
    def test_get_excel_without_filename(self, mocked_post, mocked_metadata):
        mocked_metadata.return_value = metadata

        mocked_post.return_value.__enter__.return_value = mocked_response

        self.sf = Reportforce(mocks.FakeLogin)

        self.m = mock_open()


        with patch("reportforce.report.open", self.m, create=True):
            self.excel = self.sf.get("report_id", excel=True)

        self.m.assert_called_once_with("spreadsheet.xlsx", "wb")

    @patch("reportforce.report.get_metadata")
    @patch.object(Reportforce.session, "post")
    def test_get_excel_with_filename(self, mocked_post, mocked_metadata):
        mocked_metadata.return_value = metadata

        mocked_post.return_value.__enter__.return_value = mocked_response

        self.sf = Reportforce(mocks.FakeLogin)

        self.m = mock_open()


        with patch("reportforce.report.open", self.m, create=True):
            self.excel = self.sf.get("report_id", excel="filename.xlsx")

        self.m.assert_called_once_with("filename.xlsx", "wb")


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
