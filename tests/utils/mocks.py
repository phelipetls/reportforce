import json
from pathlib import Path


class FakeLogin:
    """Fake Salesforce session object"""

    version = "47.0"
    session_id = "sessionId"
    instance_url = "dummy.salesforce.com"
    headers = {"Authorization": "Bearer sessionId"}


def get_json(json_file):
    path = Path(__file__).resolve().parent / ".." /"sample_json" / json_file
    with open(path, "r") as f:
        return json.loads(f.read())
