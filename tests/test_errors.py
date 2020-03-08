import os
import sys
import json
import unittest
import requests
import simplejson

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import Mock
from reportforce.helpers.errors import ReportError, handle_error  # noqa: E402

ok_json = {"json.return_value": [{"this json": "is ok"}]}
binary = {"json.return_value": "\x005"}


class MockErrorResponse(requests.Response):
    """Mock error response body."""

    text = '[{"errorCode": "errorCode", "message": "message"}]'


class MockInvalidJSON(requests.Response):
    text = "\x005"


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

    def test_json_decode_error(self):
        """Test binary string being passed to json parser."""
        handle_error(MockBytesResponse())

    def test_simplejson_json_decode_error(self):
        """Test binary string being passed to simplejson parser."""
        handle_error(MockInvalidJSON())


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
