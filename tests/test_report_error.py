import os
import sys
import unittest
import requests

from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.report import get_report  # noqa: E402
from utils import mocks  # noqa: E402
from reportforce.report import SessionNotFound  # noqa: E402
from reportforce.helpers.request_report import ReportError  # noqa: E402

metadata = mocks.get_json("analytics_tabular_metadata")
error = [{"errorCode": "errorCode", "message": "message"}]


class TestExceptions(unittest.TestCase):
    @patch("reportforce.report.get_metadata")
    @patch.object(requests.Session, "post")
    def test_if_raises_report_error(self, mocked_session, mocked_metadata):

        mocked_metadata.return_value = metadata

        mocked_session().json.return_value = error
        with self.assertRaises(ReportError):
            get_report("report_id", session=mocks.FakeLogin)

    def test_if_raises_session_not_found(self):
        with self.assertRaises(SessionNotFound):
            get_report("report_id")


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
