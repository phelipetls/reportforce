import os
import sys
import unittest

from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.helpers.errors import ReportError, handle_error  # noqa: E402

config = {"json.return_value": [{"errorCode": "errorCode", "message": "message"}]}


class TestExceptions(unittest.TestCase):
    def test_handle_error_hook(self):
        response = Mock(**config)

        with self.assertRaises(ReportError):
            handle_error(response)


if __name__ == "__main__":
    unittest.main()

# vi: nowrap
