import copy
import requests
import functools
import pandas as pd

from .helpers import parser
from .helpers import request

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
        Initial date in the format %Y-%m-%d.

    end : str
        Final date in the format %Y-%m-%d.

    filters : list
        List of tuples, each of which represents
        a filter: [("COL", ">=", "VALUE")].

    logic : str
        Logical filter. This is commonly needed if
        the report already has a report filter, but
        it can also be useful in general.

    session : object
        A simple-salesforce's Salesforce object or
        a reportforce.login.Login object, needed for
        authentication.

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
        set_period(start, end, metadata)
    if logic:
        set_logic(logic, metadata)
    if filters:
        set_filters(filters, metadata)

    column_labels = parser.get_column_labels_dict(metadata)
    id_index = list(column_labels.keys()).index(id_column) if id_column else None

    return pd.concat(
        map(
            lambda x: pd.DataFrame(x, columns=column_labels),
            report_generator(report_id, id_column, id_index, metadata, session),
        )
    ).reset_index()


def report_generator(
    report_id, id_column=None, id_index=None, metadata=None, session=None
):
    url = base_url.format(session.instance_url, session.version, report_id)

    report = request.request_report(url, headers=session.headers, json=metadata)
    report_cells = parser.get_cells(report)
    yield report_cells

    already_seen = ""
    while not report["allData"] and id_column:
        already_seen += ",".join(cell[id_index] for cell in report_cells)
        set_filters([(id_column, "!=", already_seen)], metadata)
        report = request.request_report(url, headers=session.headers, json=metadata)
        report_cells = parser.get_cells(report)
        yield report_cells


@functools.lru_cache(maxsize=8)
def get_metadata(report_id, session=None):
    url = (
        base_url.format(session.instance_url, session.version, report_id) + "/describe"
    )
    return requests.get(url, headers=session.headers).json()


class SessionNotFound(Exception):
    pass


operators_dict = {
    "==": "equals",
    "!=": "notEqual",
    ">": "greaterThan",
    "<": "lessThan",
    ">=": "greaterOrEqual",
    "<=": "lessOrEqual",
}


def set_filters(filters, metadata):
    for filter_ in filters:
        column, operator, value = filter_
        filter_dict = {
            "column": parser.get_column_labels_dict(metadata)[column],
            "operator": operators_dict.get(operator),
            "value": value,
        }
        metadata["reportMetadata"]["reportFilters"].append(filter_dict)


def set_logic(logic, metadata):
    metadata["reportBooleanFilter"] = logic


def set_period(start, end, metadata):
    date_filter = metadata["reportMetadata"]["standardDateFilter"]
    date_filter["startDate"] = start
    date_filter["endDate"] = end
    date_filter["durationValue"] = "CUSTOM"
