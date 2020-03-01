def handle_error(r, **kwargs):
    try:
        error = r.json()[0]
        raise ReportError(error["errorCode"], error["message"])
    except KeyError:
        pass


class ReportError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "\n\nCode: {}. Message: {}".format(self.code, self.msg)
