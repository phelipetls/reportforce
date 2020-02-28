import functools

from .report import get_report

class Reportforce:
    """Class to easily interact with Salesforce Analytics API."""

    def __init__(self, session):
        self.session = session

    @property
    def get(self):
        """Method that wraps get_report functionality."""
        return functools.update_wrapper(
            functools.partial(get_report, session=self.session), get_report
        )
