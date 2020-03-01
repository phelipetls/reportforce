import os
import sys
import unittest

from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.helpers.request_report import ReportError, handle_error  # noqa: E402

error = [{"errorCode": "errorCode", "message": "message"}]


class TestExceptions(unittest.TestCase):
    def test_handle_error_hook(self):
        mocked_response = Mock()
        mocked_response.json.return_value = error

        with self.assertRaises(ReportError):
            handle_error(mocked_response)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
