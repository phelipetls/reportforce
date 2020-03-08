import os
import sys
import json
import unittest
import requests

from unittest.mock import patch, Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.helpers.errors import ReportError, handle_error  # noqa: E402

ok_json = {"json.return_value": [{"this json": "is ok"}]}
binary = {"json.return_value": "\x005"}


class MockErrorResponse:
    """Mock error response body."""

    text = '[{"errorCode": "errorCode", "message": "message"}]'

    def json(self):
        return json.loads(self.text)


class MockBytesResponse:
    text = "\x005"

    def json(self):
        return json.loads(self.text)


class TestErrorHandling(unittest.TestCase):
    def test_handle_error_json(self):
        """Test if ReportError is raised when error-like JSON is passed."""
        with self.assertRaises(ReportError):
            handle_error(MockErrorResponse())

    def test_error_string_repr(self):
        """Check error string representation."""
        try:
            handle_error(MockErrorResponse())
        except ReportError as error:
            self.assertEqual(str(error), "\nCode: errorCode. Message: message")

    def test_expections_binary_string(self):
        """Test binary string being passed to simplejson parser."""
        handle_error(MockBytesResponse())

if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
