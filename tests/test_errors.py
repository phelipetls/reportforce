import json
import unittest
import requests

from reportforce.helpers.errors import ReportError, handle_error


class ErrorResponse(requests.Response):
    """Simulate a response with a error response as its body."""

    text = '[{"errorCode": "errorCode", "message": "message"}]'


class TestSalesforceErrorJson(unittest.TestCase):
    """Test if ReportError is raised when error-like JSON is passed."""

    def test_handle_error_json(self):
        with self.assertRaises(ReportError):
            handle_error(ErrorResponse())

    def test_error_string_repr(self):
        """Check error string representation."""
        try:
            handle_error(ErrorResponse())
        except ReportError as error:
            self.assertEqual(str(error), "\nCode: errorCode. Message: message")


class BytesResponse:
    """Simulate a response with a body with byte-content."""
    text = "\x005"

    def json(self):
        return json.loads(self.text)


class TestErrorBytesString(unittest.TestCase):
    """Test binary string being passed to json parser."""

    def test_json_decode_error(self):
        response = BytesResponse()

        handle_error(response)


class InvalidJsonResponse(requests.Response):
    text = "{invalid: json"


class TestErrorInvalidJsonString(unittest.TestCase):
    """Test binary string being passed to simplejson parser."""

    def test_simplejson_json_decode_error(self):
        response = InvalidJsonResponse()

        handle_error(response)


if __name__ == "__main__":
    unittest.main(failfast=True)

# vi: nowrap
