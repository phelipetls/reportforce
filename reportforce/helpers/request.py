import requests

s = requests.Session()

def request_report(url, **kwargs):
    report = s.post(url, **kwargs).json()
    try:
        raise ReportError(report[0]["errorCode"], report[0]["message"])
    except KeyError:
        return report

class ReportError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "\n\nCode: {}. Message: {}".format(self.code, self.msg)
