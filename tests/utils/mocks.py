import json

from pathlib import Path
from unittest.mock import patch


def get_json(json_file):
    path = Path(__file__).resolve().parent / ".." / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())


def mock_get_metadata(metadata):
    metadata_config = {"return_value": get_json(metadata)}
    return patch("reportforce.api.Reportforce.get_metadata", **metadata_config)


def mock_login():
    soap_login_config = {"return_value": ("sessionId", "dummy.salesforce.com")}
    return patch("reportforce.login.soap_login", **soap_login_config)


def generate_reports(second):
    """Pick a report, make its allData attribute false, so
    as to simulate an incomplete Salesforce report to force
    keeping getting reports.

    Then the second report will have allData attribute set
    to true, and the iteration will stop.
    """
    first = second.copy()
    first["allData"] = False
    return [first, second]
