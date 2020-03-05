import re
import copy
import requests
import functools
import numpy as np
import pandas as pd

from .helpers import errors
from .helpers import parsers
from .helpers import filtering
from .helpers import report_generator

URL = "https://{}/services/data/v{}/analytics/reports/{}"


class Reportforce:
    """Class to interact with Salesforce Analytics API."""

    session = requests.Session()
    session.hooks["response"].append(errors.handle_error)

    def __init__(self, auth):
        self.version = auth.version
        self.instance_url = auth.instance_url

        self.session.headers.update(auth.headers)

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
        metadata = copy.deepcopy(get_metadata(report_id, self))

        if start or end:
            filtering.set_period(start, end, date_column, metadata)
        if logic:
            filtering.set_logic(logic, metadata)
        if filters:
            filtering.set_filters(filters, metadata)

        if excel:
            return get_excel(report_id, excel, metadata, self, **kwargs)

        report_format = metadata["reportMetadata"]["reportFormat"]

        if report_format == "TABULAR":
            return get_tabular_reports(report_id, id_column, metadata, self, **kwargs)
        elif report_format == "SUMMARY":
            return get_summary_reports(report_id, id_column, metadata, self, **kwargs)
        elif report_format == "MATRIX":
            return get_matrix_reports(report_id, id_column, metadata, self, **kwargs)

    def get_total(self, report_id):
        url = URL.format(self.instance_url, self.version, report_id)

        report = self.session.get(url, params={"includeDetails": "false"}).json()
        return parsers.get_report_total(report)


def get_excel(report_id, excel, metadata, salesforce, **kwargs):
    """Download report as formatted Excel spreadsheet.

    Parameters
    ----------
    report_id : str
        A report unique identifier.

    excel : bool or str
        If a non-empty string, it will be used as the filename.
        If True, the workbook is automatically named.

    salesforce : object
        An instance of simple_salesforce.Salesforce or
        reportforce.login.Login, needed for authentication.
    """
    url = URL.format(salesforce.instance_url, salesforce.version, report_id)

    headers = salesforce.session.headers.copy()

    headers.update(
        {"Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    )

    with salesforce.session.post(url, headers=headers, json=metadata, stream=True, **kwargs) as r:
        if isinstance(excel, str):
            filename = excel
        else:
            string = r.headers["Content-Disposition"]
            pattern = 'filename="(.*)"'
            filename = re.search(pattern, string).group(1)

        with open(filename, "wb") as excel_file:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    excel_file.write(chunk)


@report_generator.report_generator
def get_tabular_reports(url, metadata=None, salesforce=None, **kwargs):
    """Request and parse a tabular report.

    Parameters
    ----------
    url : str
        Report url.

    metadata : dict
        Used for filtering.

    session : object
        Used for authentication.

    Returns
    -------
    tuple
        JSON response body parsed as a dict.
        Report data cells parsed as a list.
        Indices to be used in the DataFrame.
    """
    tabular = salesforce.session.post(url, json=metadata, **kwargs).json()

    tabular_cells = parsers.get_tabular_cells(tabular)
    indices = None  # no meaningful indices here

    return tabular, tabular_cells, indices


@report_generator.report_generator
def get_matrix_reports(url, metadata, salesforce, **kwargs):
    """Request and parse a matrix report.

    Parameters
    ----------
    url : str
        Report url.

    metadata : dict
        Used for filtering.

    salesforce : object
        Used for authentication.

    Returns
    -------
    tuple
        JSON response body parsed as a dict.
        Report data cells parsed as a list.
        Indices to be used in the DataFrame.
    """
    matrix = salesforce.session.post(url, json=metadata, **kwargs).json()

    if len(matrix["factMap"]) == 1:
        return matrix, [], None

    matrix_cells = np.array(parsers.get_matrix_cells(matrix))

    groupings_down = matrix["groupingsDown"]["groupings"]
    names = parsers.get_groupings_labels(matrix, "groupingsDown")
    indices = pd.MultiIndex.from_tuples(parsers.get_groups(groupings_down), names=names)

    columns = parsers.get_columns(matrix)

    matrix_cells.shape = (len(indices), len(columns))
    return matrix, matrix_cells, indices


@report_generator.report_generator
def get_summary_reports(url, metadata, salesforce, **kwargs):
    """Request and parse a summary report.

    Parameters
    ----------
    url : str
        Report url.

    metadata : dict
        Used for filtering.

    salesforce : object
        Used for authentication.

    Returns
    -------
    tuple
        JSON response body parsed as a dict.
        Report fact map parsed as a list.
        Indices to be used in the DataFrame.
    """
    summary = salesforce.session.post(url, json=metadata, **kwargs).json()

    if len(summary["factMap"]) == 1:
        return summary, [], None

    summary_cells, cells_by_group = parsers.get_summary_cells(summary)
    indices = parsers.get_summary_indices(summary, cells_by_group)

    return summary, summary_cells, indices


@functools.lru_cache(maxsize=8)
def get_metadata(report_id, salesforce=None):
    """Request report metadata.

    Parameters
    ----------
    report_id : str
        A report unique identifier.

    session : object (optional)
        ** TODO : fix documentation. **

    Returns
    -------
    dict
        The JSON response body as a dictionary.
    """
    url = (
        URL.format(salesforce.instance_url, salesforce.version, report_id)
        + "/describe"  # noqa: W503
    )
    return salesforce.session.get(url).json()
