import os
import sys
import unittest

from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import Reportforce  # noqa: E402
from utils import mocks  # noqa: E402

mock_open = mock_open()
mock_metadata = mocks.get_json("analytics_tabular_metadata")


class MockResponse:
    headers = {"Content-Disposition": 'attachment; filename="spreadsheet.xlsx"'}

    def iter_content(chunk_size):
        return b"1,2,3\na,b,c"


metadata_config = {"return_value": mock_metadata}
post_config = {"return_value.__enter__.return_value": MockResponse}


class TestExcelWithoutFilename(unittest.TestCase):
    def setUp(self):
        self.get_metadata = patch("reportforce.report.get_metadata", **metadata_config)
        self.get_metadata.start()

        self.post = patch.object(Reportforce.session, "post", **post_config)
        self.post.start()

        self.rf = Reportforce(mocks.FakeLogin)

    def test_get_excel_without_filename(self):
        """When no filename is given, the one in the headers is used."""

        with patch("reportforce.report.open", mock_open, create=True):
            self.rf.get_report("report_id", excel=True)

        mock_open.assert_called_with("spreadsheet.xlsx", "wb")

    def test_get_excel_with_filename(self):
        """When a filename is given, it is used."""

        with patch("reportforce.report.open", mock_open, create=True):
            self.rf.get_report("report_id", excel="filename.xlsx")

        mock_open.assert_called_with("filename.xlsx", "wb")

    def tearDown(self):
        self.get_metadata.stop()
        self.post.stop()


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
