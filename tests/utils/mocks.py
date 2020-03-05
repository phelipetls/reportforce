import json
import unittest

from pathlib import Path
from unittest.mock import patch


def get_json(json_file):
    path = Path(__file__).resolve().parent / ".." / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())

def mock_get_metadata(metadata):
    metadata_config = {"return_value": get_json(metadata)}
    return patch("reportforce.reportforce.Reportforce.get_metadata", **metadata_config)

def mock_login():
    soap_login_config = {"return_value": ("sessionId", "dummy.salesforce.com")}
    return patch("reportforce.login.soap_login", **soap_login_config)
