def handle_error(response, **kwargs):
    try:
        error = response.json()[0]
        raise ReportError(error["errorCode"], error["message"])
    except (KeyError, ValueError):
        pass


class ReportError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "\nCode: {}. Message: {}".format(self.code, self.msg)
