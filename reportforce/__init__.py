import requests
import functools

from .report import get_report
from .helpers.request_report import handle_error


class Reportforce:
    """Class to easily interact with Salesforce Analytics API."""

    session = requests.Session()
    session.hooks["response"].append(handle_error)

    def __init__(self, auth):
        self.version = auth.version
        self.instance_url = auth.instance_url
        self.headers = auth.headers


    @property
    def get(self):
        """Method that wraps get_report functionality."""
        return functools.update_wrapper(
            functools.partial(get_report, salesforce=self), get_report
        )
