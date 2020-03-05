import json
import unittest

from pathlib import Path
from unittest.mock import patch


def get_json(json_file):
    path = Path(__file__).resolve().parent / ".." / "sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())
