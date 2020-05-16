import re
import copy
import requests
import functools
import pandas as pd

from urllib.parse import urljoin

from .login import Salesforce

from .helpers import errors
from .helpers.metadata import Metadata
from .helpers.tabular import Tabular
from .helpers.matrix import Matrix
from .helpers.summary import Summary

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

    def _get_report_url(self, report_id):
        return urljoin(self.url, report_id)

    def get_report(
        self,
        report_id,
        id_column=None,
        date_column=None,
        start=None,
        end=None,
        date_duration=None,
        ignore_date_filter=False,
        filters=[],
        logic=None,
        excel=None,
        **kwargs,
    ):
        """Function to get a Salesforce report into a DataFrame.

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

        ignore_date_filter : bool (optional)
            Whether or not you want to ignore the standard date filter.

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
        self.report_url = self._get_report_url(report_id)
        self.id_column = id_column

        self.metadata = copy.deepcopy(self.get_metadata(report_id))

        self.metadata.boolean_filter = logic
        self.metadata.report_filters = filters

        if ignore_date_filter:
            self.metadata.ignore_date_filter()
        elif date_duration:
            self.metadata.set_date_duration(date_duration)
        else:
            if start:
                self.metadata.date_start = start
            if end:
                self.metadata.date_end = end
            if date_column:
                self.metadata.date_column = date_column
            if (start or end or date_column):
                self.metadata.date_duration = "CUSTOM"

        if excel:
            return self._save_spreadsheet(excel)

        self.parser = self._get_parser()
        report = pd.concat(self._generate_reports(**kwargs))

        return self._reset_index(report)

    def _get_metadata_url(self, report_id):
        return urljoin(self.url, report_id + "/describe")

    @functools.lru_cache(maxsize=8)
    def get_metadata(self, report_id):
        """Get a report metadata, used to manipulate reports."""
        url = self._get_metadata_url(report_id)

        return Metadata(self.session.get(url).json())

    def _generate_reports(self, **kwargs):
        report = self._get_report(**kwargs)
        df = report.to_dataframe()
        yield df

        while not report.all_data and self.id_column:
            self._filter_past_values(df)

            report = self._get_report(**kwargs)
            df = report.to_dataframe()
            yield df

    def _get_report(self, **kwargs):
        response = self.session.post(
            self.report_url, json=self.metadata, **kwargs
        ).json()
        return self.parser(response)

    _parsers = {"TABULAR": Tabular, "MATRIX": Matrix, "SUMMARY": Summary}

    def _get_parser(self):
        report_format = self.metadata.report_format
        return self._parsers[report_format]

    def _filter_past_values(self, df):
        new_filter = (self.id_column, "!=", df[self.id_column])
        self.metadata.report_filters = [new_filter]
        self.metadata.increment_boolean_filter()

    def _reset_index(self, df):
        """Unless it is a pandas.MultiIndex."""
        if not isinstance(df.index, pd.MultiIndex):
            df = df.reset_index(drop=True)
        return df

    EXCEL_HEADERS = {
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    def _save_spreadsheet(self, excel):
        excel_headers = self._get_excel_headers()

        with self.session.post(
            self.report_url, headers=excel_headers, json=self.metadata, stream=True
        ) as response:
            if isinstance(excel, str):
                filename = excel
            elif excel:
                content_disposition = response.headers["Content-Disposition"]
                filename = re.search(r'filename="(.*)"', content_disposition).group(1)

            with open(filename, "wb") as spreadsheet:
                for chunk in response.iter_content(chunk_size=512 * 1024):
                    if chunk:
                        spreadsheet.write(chunk)

    def _get_excel_headers(self):
        excel_headers = self.session.headers.copy()
        excel_headers.update(self.EXCEL_HEADERS)
        return excel_headers
