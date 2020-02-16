import requests

s = requests.Session()


def request_report(url, **kwargs):
    """
    A wrapper around requests.post designed
    to extract data from Salesforce.

    Returns
    -------
    dict
        A dictionary with the response body
        contents to the requested report.

    Raises
    ------
    ReportError
        If the response body is an error JSON.
    """
    report = s.post(url, **kwargs).json()
    try:
        raise ReportError(report[0]["errorCode"], report[0]["message"])
    except KeyError:
        return report

def request_excel(url, **kwargs):
    """
    A wrapper around requests.get designed
    to extract data from Salesforce.
    """
    report = s.get(url, **kwargs)
    report.raise_for_status()
    return report


class ReportError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "\n\nCode: {}. Message: {}".format(self.code, self.msg)
