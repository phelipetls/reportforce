import re
import copy
import functools
import numpy as np
import pandas as pd

from .helpers import parsers
from .helpers import request_report
from .helpers import filtering
from .helpers import report_generator

base_url = "https://{}/services/data/v{}/analytics/reports/{}"


def get_report(
    report_id,
    id_column=None,
    date_column=None,
    start=None,
    end=None,
    filters=[],
    logic=None,
    session=None,
    excel=None,
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

    session : object (optional)
        An instance of simple_salesforce.Salesforce or reportforce.login.Login
        to authenticate the requests.

    Returns
    -------
    DataFrame
        A DataFrame contaning the records from the report.
    """
    if session is None:
        raise SessionNotFound

    metadata = copy.deepcopy(get_metadata(report_id, session))

    if start or end:
        filtering.set_period(start, end, date_column, metadata)
    if logic:
        filtering.set_logic(logic, metadata)
    if filters:
        filtering.set_filters(filters, metadata)

    if excel:
        return get_excel(report_id, excel, metadata, session)

    report_format = metadata["reportMetadata"]["reportFormat"]

    if report_format == "TABULAR":
        return get_tabular_reports(report_id, id_column, metadata, session)
    elif report_format == "SUMMARY":
        return get_summary_reports(report_id, id_column, metadata, session)
    elif report_format == "MATRIX":
        return get_matrix_reports(report_id, id_column, metadata, session)


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


def get_excel(report_id, excel, metadata, session):
    """Download report as formatted Excel spreadsheet.

    Parameters
    ----------
    report_id : str
        A report unique identifier.

    excel : bool or str
        If a non-empty string, it will be used as the filename.
        If True, the workbook is automatically named.

    session : object
        An instance of simple_salesforce.Salesforce or
        reportforce.login.Login, needed for authentication.
    """
    url = base_url.format(session.instance_url, session.version, report_id)

    headers = session.headers.copy()

    spreadsheet_headers = {"Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    headers.update(spreadsheet_headers)

    with request_report.POST(url, headers=headers, json=metadata, stream=True) as r:
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
def get_tabular_reports(url, metadata=None, session=None):
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
    tabular = request_report.POST(url, headers=session.headers, json=metadata).json()

    tabular_cells = parsers.get_tabular_cells(tabular)
    indices = None  # no meaningful indices here

    return tabular, tabular_cells, indices


@report_generator.report_generator
def get_matrix_reports(url, metadata, session):
    """Request and parse a matrix report.

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
    matrix = request_report.POST(url, headers=session.headers, json=metadata).json()

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
def get_summary_reports(url, metadata, session):
    """Request and parse a summary report.

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
        Report fact map parsed as a list.
        Indices to be used in the DataFrame.
    """
    summary = request_report.POST(url, headers=session.headers, json=metadata).json()

    if len(summary["factMap"]) == 1:
        return summary, [], None

    summary_cells, cells_by_group = parsers.get_summary_cells(summary)
    indices = parsers.get_summary_indices(summary, cells_by_group)

    return summary, summary_cells, indices


@functools.lru_cache(maxsize=8)
def get_metadata(report_id, session=None):
    """Request report metadata.

    Parameters
    ----------
    report_id : str
        A report unique identifier.

    session : object (optional)
        An instance of simple_salesforce.Salesforce or reportforce.login.Login,
        used for authentication.

    Returns
    -------
    dict
        The JSON response body as a dictionary.
    """
    if session is None:
        raise SessionNotFound

    url = (
        base_url.format(session.instance_url, session.version, report_id) + "/describe"
    )
    return request_report.GET(url, headers=session.headers).json()


class SessionNotFound(Exception):
    pass
