import requests

s = requests.Session()


def handle_error(request):
    """
    Decorator to handle Salesforce request errors.
    """

    def handler(*args, **kwargs):
        response = request(*args, **kwargs)
        if response.status_code != 200:
            try:
                error = response.json()[0]
                raise ReportError(error["errorCode"], error["message"])
            except KeyError:
                response.raise_for_status()
        else:
            return response

    return handler


@handle_error
def POST(url, **kwargs):
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
        If the response body is a JSON containing
        an error message.
    """
    return s.post(url, **kwargs)


@handle_error
def GET(url, **kwargs):
    """
    A wrapper around requests.get designed
    to extract data from Salesforce.

    Returns
    -------
    dict
        A dictionary with the response body
        contents to the requested report.

    Raises
    ------
    ReportError
        If the response body is a JSON containing
        an error message.
    """
    return s.get(url, **kwargs)


class ReportError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "\n\nCode: {}. Message: {}".format(self.code, self.msg)
