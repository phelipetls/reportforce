import re
import copy
import functools
import itertools
import numpy as np
import pandas as pd

from .helpers import parsers
from .helpers import request_report
from .helpers import filtering

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
        return get_matrix_report(report_id, metadata, session)


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

    excel = request_report.GET(url, headers=headers)

    if isinstance(excel, str):
        filename = excel
    else:
        string = excel.headers["Content-Disposition"]
        pattern = 'filename="(.*)"'
        filename = re.search(pattern, string).group(1)

    with open(filename, "wb") as excel_file:
        excel_file.write(excel.content)

    return


def get_tabular_report(report_id, id_column, metadata, session):
    """
    Auxiliary function to deal with tabular reports
    """
    tabular_generator = tabular_report_generator(
        report_id, id_column, metadata, session
    )
    return pd.concat(tabular_generator).reset_index(drop=True)


def tabular_report_generator(report_id, id_column=None, metadata=None, session=None):
    """
    Auxiliary function to generate tabular reports until
    all data is returned, i.e. until "allData" in the
    JSON response body is "true".
    """
    url = base_url.format(session.instance_url, session.version, report_id)

    report = request_report.POST(url, headers=session.headers, json=metadata).json()
    report_cells = parsers.get_tabular_cells(report)
    columns_labels = parsers.get_column_labels(metadata)

    yield pd.DataFrame(report_cells, columns=columns_labels)

    if id_column:
        id_index = list(columns_labels.keys()).index(id_column)

        already_seen = ""
        filtering.set_filters([(id_column, "!=", already_seen)], metadata)
        filtering.increment_logical_filter(metadata)

    while not report["allData"] or not id_column:
        # getting what is need to build the dataframe
        report = request_report.POST(url, headers=session.headers, json=metadata).json()
        report_cells = parsers.get_tabular_cells(report)

        # filtering out already seen values
        if id_column:
            already_seen += ",".join(cell[id_index] for cell in report_cells)
            filtering.update_filter(-1, "value", already_seen, metadata)

        yield pd.DataFrame(report_cells, columns=columns_labels)


def get_matrix_report(report_id, metadata, session):
    """
    Auxiliary function to deal with matrix reports
    """
    url = base_url.format(session.instance_url, session.version, report_id)
    matrix = request_report.POST(url, headers=session.headers, json=metadata).json()

    indices = pd.MultiIndex.from_tuples(
        parsers.get_groups(matrix["groupingsDown"]["groupings"])
    )
    columns = pd.MultiIndex.from_tuples(
        parsers.get_groups(matrix["groupingsAcross"]["groupings"])
    )

    report_cells = np.array(parsers.get_matrix_cells(matrix))
    report_cells.shape = (len(indices), len(columns))
    return pd.DataFrame(report_cells, index=indices, columns=columns)


def get_summary_report(report_id, id_column, metadata, session):
    """
    Auxiliary function to deal with summary reports
    """
    summary_generator = summary_report_generator(
        report_id, id_column, metadata, session
    )
    return pd.concat(summary_generator)


def summary_report_generator(report_id, id_column, metadata, session):
    url = base_url.format(session.instance_url, session.version, report_id)

    summary = request_report.POST(url, headers=session.headers, json=metadata).json()
    summary_cells, cells_by_group = parsers.get_summary_cells(summary)
    indices = summary_get_indices(summary, cells_by_group)
    columns_labels = parsers.get_column_labels(metadata)

    yield pd.DataFrame(summary_cells, index=indices, columns=columns_labels)

    if id_column:
        id_index = list(columns_labels.keys()).index(id_column)

        already_seen = ""
        filtering.set_filters([(id_column, "!=", already_seen)], metadata)
        filtering.increment_logical_filter(metadata)

    while not summary["allData"] or not id_column:
        summary = request_report.POST(
            url, headers=session.headers, json=metadata
        ).json()

        # getting what is need to build dataframe
        summary_cells, cells_by_group = parsers.get_summary_cells(summary)
        indices = summary_get_indices(summary, cells_by_group)

        # filtering out already seen values
        if id_column:
            already_seen += ",".join(cell[id_index] for cell in summary_cells)
            filtering.update_filter(-1, "value", already_seen, metadata)

        yield pd.DataFrame(summary_cells, index=indices, columns=columns_labels)


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
