import copy
import requests
import functools
import itertools
import numpy as np
import pandas as pd

from .helpers import parsers
from .helpers import request
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

    metadata = copy.deepcopy(get_metadata(report_id, session))

    if start and end:
        filtering.set_period(start, end, date_column, metadata)
    if logic:
        filtering.set_logic(logic, metadata)
    if filters:
        filtering.set_filters(filters, metadata)

    if metadata["reportMetadata"]["reportFormat"] == "TABULAR":
        return get_tabular_report(report_id, id_column, metadata, session)
    elif metadata["reportMetadata"]["reportFormat"] == "SUMMARY":
        return get_summary_report(report_id, metadata, session)
    elif metadata["reportMetadata"]["reportFormat"] == "MATRIX":
        return get_matrix_report(report_id, metadata, session)


def get_tabular_report(report_id, id_column, metadata, session):
    column_labels = parsers.get_column_labels(metadata)
    id_index = list(column_labels.keys()).index(id_column) if id_column else None
    return pd.concat(
        map(
            lambda x: pd.DataFrame(x, columns=column_labels),
            tabular_report_generator(report_id, id_column, id_index, metadata, session),
        )
    ).reset_index()


def tabular_report_generator(
    report_id, id_column=None, id_index=None, metadata=None, session=None
):
    """
    Auxiliary function to generate reports until
    all data is returned, i.e. until "allData" in the
    JSON response body is "true".
    """
    url = base_url.format(session.instance_url, session.version, report_id)

    report = request.request_report(url, headers=session.headers, json=metadata)
    report_cells = parsers.get_tabular_cells(report)
    yield report_cells

    already_seen = ""
    while not report["allData"] and id_column:
        already_seen += ",".join(cell[id_index] for cell in report_cells)
        filtering.set_filters([(id_column, "!=", already_seen)], metadata)
        report = request.request_report(url, headers=session.headers, json=metadata)
        report_cells = parsers.get_tabular_cells(report)
        yield report_cells


def get_matrix_report(report_id, metadata, session):
    url = base_url.format(session.instance_url, session.version, report_id)
    matrix = request.request_report(url, headers=session.headers, json=metadata)

    indices = pd.MultiIndex.from_tuples(
        parsers.get_groups(matrix["groupingsDown"]["groupings"])
    )
    columns = pd.MultiIndex.from_tuples(
        parsers.get_groups(matrix["groupingsAcross"]["groupings"])
    )

    cells = np.array(parsers.get_matrix_cells(matrix))
    cells.shape = (len(indices), len(columns))
    return pd.DataFrame(cells, index=indices, columns=columns)


def get_summary_report(report_id, metadata, session):
    url = base_url.format(session.instance_url, session.version, report_id)
    summary = request.request_report(url, headers=session.headers, json=metadata)

    cells, number_cell_by_group = parsers.get_summary_cells(summary)

    groups = parsers.get_groups(summary["groupingsDown"]["groupings"])

    repeat_groups = lambda x, z: x * z
    groups_frequency_pairs = zip(groups, number_cell_by_group)
    repeated_groups = itertools.chain.from_iterable(
        itertools.starmap(itertools.repeat, groups_frequency_pairs)
    )

    multi_index = pd.MultiIndex.from_tuples(repeated_groups)

    columns = parsers.get_column_labels(metadata)

    return pd.DataFrame(cells, index=multi_index, columns=columns)


@functools.lru_cache(maxsize=8)
def get_metadata(report_id, session=None):
    """
    Function to get a report metadata information,
    which is used for filtering reports.
    """
    url = (
        base_url.format(session.instance_url, session.version, report_id) + "/describe"
    )
    return requests.get(url, headers=session.headers).json()


class SessionNotFound(Exception):
    pass
