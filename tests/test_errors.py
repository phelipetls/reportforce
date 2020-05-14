import json
import pytest
import requests

from reportforce.helpers.errors import ReportError, handle_error


class ResponseWithApiError(requests.Response):
    text = '[{"errorCode": "errorCode", "message": "message"}]'


def test_report_error():
    """Handle_error hook should raise ReportError only for error-like JSON."""
    with pytest.raises(ReportError):
        handle_error(ResponseWithApiError())


def test_report_error_string_representation():
    """Test ReportError string representation."""
    with pytest.raises(ReportError) as report_error:
        handle_error(ResponseWithApiError())

    assert str(report_error.value) == "\nCode: errorCode. Message: message"


class ResponseWithBinaryContent:
    text = "\x005"

    def json(self):
        return json.loads(self.text)


def test_report_error_should_not_raise_with_binary_content():
    """Shouldn't raise for responses with binary content."""
    handle_error(ResponseWithBinaryContent())


class ResponseWithInvalidJSON(requests.Response):
    text = "{invalid: json"


def test_report_error_should_not_raise_with_invalid_json():
    """Shouldn't raise for responses with invalid JSONs."""

    handle_error(ResponseWithInvalidJSON())
