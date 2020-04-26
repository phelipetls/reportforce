import json

from pathlib import Path


def read_data(data):
    path = Path(__file__).resolve().parent / "data" / data

    with open(path, "r") as f:
        return f.read()


def read_json(data):
    return json.loads(read_data(data))


class MockJsonResponse:
    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.status_code = 200

    def json(self):
        return self.data
