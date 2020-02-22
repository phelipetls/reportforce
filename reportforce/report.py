import re
import copy
import functools
import itertools
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
    """
    Function to retrieve a Salesforce tabular report
    into a DataFrame.

    Parameters
    ----------
    report_id : str
        Report unique identifier.

    id_column : str
        Column name (label) which has unique values
        for each row, i.e., a key. This is needed to
        as a workaround the Analytics API's 2000 row
        limitation.

    date_column : str
        Date column name (label).

    start : str
        Initial date string, passed into dateutil.parser.parse.

    end : str
        Final date string, passed into dateutil.parser.parse.

    filters : list
        List of tuples, each of which represents
        a filter: [("COL", ">=", "VALUE")].

    logic : str
        Logical filter. This is commonly needed if
        the report already has a report filter, but
        it can also be useful in general.

    session : object
        An instance of simple_salesforce.Salesforce or
        reportforce.login.Login, needed for authentication.

    Returns
    -------
    DataFrame
        A DataFrame contaning the records from
        the report.
    """
    if not session:
        raise SessionNotFound

    if excel:
        return get_excel(report_id, excel, session)

    metadata = copy.deepcopy(get_metadata(report_id, session))

    if start and end:
        filtering.set_period(start, end, date_column, metadata)
    if logic:
        filtering.set_logic(logic, metadata)
    if filters:
        filtering.set_filters(filters, metadata)

    report_format = metadata["reportMetadata"]["reportFormat"]

    if report_format == "TABULAR":
        return get_tabular_report(report_id, id_column, metadata, session)
    elif report_format == "SUMMARY":
        return get_summary_report(report_id, id_column, metadata, session)
    elif report_format == "MATRIX":
        return get_matrix_report(report_id, id_column, metadata, session)


def get_excel(report_id, excel, session):
    """
    Auxiliary function to download a formatted
    Excel spreadsheet of the report.

    Parameters
    ----------
    report_id : str

    excel : bool or str
        If a non-empty string, it will serve as the filename.
        If True, it will write to the filename Salesforce provides.

    session : object
        An instance of simple_salesforce.Salesforce or
        reportforce.login.Login, needed for authentication.
    """
    url = base_url.format(session.instance_url, session.version, report_id)

    spreadsheet_header = {
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    headers = session.headers.copy()
    headers.update(spreadsheet_header)

    response = request_report.GET(url, headers=headers)

    if isinstance(excel, str):
        filename = excel
    else:
        string = response.headers["Content-Disposition"]
        pattern = 'filename="(.*)"'
        filename = re.search(pattern, string).group(1)

    with open(filename, "wb") as excel_file:
        excel_file.write(response.content)

    return


def get_tabular_report(report_id, id_column, metadata, session):
    """
    Auxiliary function to deal with tabular reports
    """
    tabular_generator = tabular_report_generator(
        report_id, id_column, metadata, session
    )
    return pd.concat(tabular_generator).reset_index(drop=True)


@report_generator.report_generator
def tabular_report_generator(url, metadata=None, session=None):
    """
    Auxiliary function to generate tabular reports until
    all data is returned, i.e. until "allData" in the
    JSON response body is "true".
    """
    tabular = request_report.POST(url, headers=session.headers, json=metadata).json()
    tabular_cells = parsers.get_tabular_cells(tabular)
    indices = None
    return tabular, tabular_cells, indices



def get_matrix_report(report_id, id_column, metadata, session):
    """
    Auxiliary function to deal with matrix reports
    """
    matrix_generator = matrix_report_generator(report_id, id_column, metadata, session)
    return pd.concat(matrix_generator)


@report_generator.report_generator
def matrix_report_generator(url, metadata, session):
    matrix = request_report.POST(url, headers=session.headers, json=metadata).json()

    if len(matrix["factMap"]) == 1:
        return pd.DataFrame()

    matrix_cells = np.array(parsers.get_matrix_cells(matrix))

    groupings_down = matrix["groupingsDown"]["groupings"]
    indices = pd.MultiIndex.from_tuples(parsers.get_groups(groupings_down))

    columns = parsers.get_columns(matrix)

    matrix_cells.shape = (len(indices), len(columns))
    return matrix, matrix_cells, indices


def get_summary_report(report_id, id_column, metadata, session):
    """
    Auxiliary function to deal with summary reports
    """
    summary_generator = summary_report_generator(
        report_id, id_column, metadata, session
    )
    return pd.concat(summary_generator)


@report_generator.report_generator
def summary_report_generator(url, metadata, session):
    summary = request_report.POST(url, headers=session.headers, json=metadata).json()

    if len(summary["factMap"]) == 1:
        return summary, [], None

    summary_cells, cells_by_group = parsers.get_summary_cells(summary)
    indices = summary_get_indices(summary, cells_by_group)

    return summary, summary_cells, indices


def summary_get_indices(summary, cells_by_group):
    groups = parsers.get_groups(summary["groupingsDown"]["groupings"])
    groups_frequency_pairs = zip(groups, cells_by_group)

    repeated_groups = itertools.chain.from_iterable(
        itertools.starmap(itertools.repeat, groups_frequency_pairs)
    )

    return pd.MultiIndex.from_tuples(repeated_groups)


@functools.lru_cache(maxsize=8)
def get_metadata(report_id, session=None):
    """
    Function to get a report metadata information,
    which is used for filtering reports.
    """
    if not session:
        raise SessionNotFound

    url = (
        base_url.format(session.instance_url, session.version, report_id) + "/describe"
    )
    return request_report.GET(url, headers=session.headers).json()


class SessionNotFound(Exception):
    pass
