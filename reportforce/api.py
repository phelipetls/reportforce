import copy
import urllib
import requests
import functools

from .login import Salesforce

from .helpers import errors
from .helpers import parsers

from .helpers.sf_filters import set_filters, set_period, set_logic

from .report import (
    get_excel,
    get_tabular_reports,
    get_summary_reports,
    get_matrix_reports,
)

URL = "https://{}/services/data/v{}/analytics/reports/"


class Reportforce(Salesforce):
    """Class to interact with the Salesforce Analytics API.

    Attributes
    ----------
    url : str
        Salesforce instance/server URL.

    session : requests.Session
        Session used for making http requests.

    Methods
    -------
    get_report : pandas.DataFrame
        Get a report as a DataFrame.

    get_total : int, float
        Get the grand total of a report.

    get_metadata : dict
        Get a report metadata.
    """

    session = requests.Session()
    session.hooks["response"].append(errors.handle_error)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = URL.format(self.instance_url, self.version)

        self.session.headers.update(self.headers)

    def get_report(
        self,
        report_id,
        id_column=None,
        date_column=None,
        start=None,
        end=None,
        filters=[],
        logic=None,
        excel=None,
        **kwargs
    ):
        """Function to get a Salesforce tabular report into a DataFrame.

        Parameters
        ----------
        report_id : str
            A report unique identifier.

        id_column : str (optional)
            Column name which has unique values for each row. This is needed as
            a workaround to the Analytics API's 2000 row limitation.

        date_column : str (optional)
            Date column name.

        start : str (optional)
            Initial date string, passed into dateutil.parser.parse. Must start with
            the day.

        end : str (optional)
            End date string, passed into dateutil.parser.parse. Must start with
            the day.

        filters : list (optional)
            List of tuples, each of which represents a filter:
            [("column", ">=", "value")].

        logic : str (optional)
            Logical filter. This is commonly needed if the report already has a
            report filter, but it can also be useful in case you add more filters.

        excel : bool, str (optional)
            Whether or not you want to save the report in a Excel file. If a
            non-empty string is passed, it will be used as the filename. If True,
            the workbook will be automatically named.

        Returns
        -------
        DataFrame
            A DataFrame contaning the records from the report.

        Raises
        ------
        ReportError
            If there is an error-like JSON string in the reponse body.
        """
        self.metadata = copy.deepcopy(self.get_metadata(report_id))

        if start or end:
            set_period(start, end, date_column, self.metadata)
        if logic:
            set_logic(logic, self.metadata)
        if filters:
            set_filters(filters, self.metadata)

        if excel:
            return get_excel(report_id, excel, self.metadata, self, **kwargs)

        report_format = self.metadata["reportMetadata"]["reportFormat"]

        args = (report_id, id_column, self.metadata, self)

        if report_format == "TABULAR":
            return get_tabular_reports(*args, **kwargs)
        elif report_format == "SUMMARY":
            return get_summary_reports(*args, **kwargs)
        else:
            return get_matrix_reports(*args, **kwargs)

    def get_total(self, report_id):
        """Get a report grand total."""
        url = urllib.parse.urljoin(self.url, report_id)

        report = self.session.get(url, params={"includeDetails": "false"}).json()
        return parsers.get_report_total(report)

    @functools.lru_cache(maxsize=8)
    def get_metadata(self, report_id):
        """Get a report metadata, used to manipulate reports."""
        url = urllib.parse.urljoin(self.url, report_id + "/describe")
        return self.session.get(url).json()
