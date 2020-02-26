import re

from . import parsers
from dateutil import parser

operators_dict = {
    "==": "equals",
    "!=": "notEqual",
    ">": "greaterThan",
    "<": "lessThan",
    ">=": "greaterOrEqual",
    "<=": "lessOrEqual",
    "contains": "contains",
    "not contains": "notContain",
    "startswith": "startsWith",
}


def set_filters(filters, metadata):
    """
    Auxiliary function to append a dictionary
    (that represents a column filter) into a
    list of dicts.
    """
    for filter_ in filters:
        column, operator, value = filter_
        filter_dict = {
            "column": parsers.get_columns_labels(metadata)[column],
            "operator": operators_dict.get(operator),
            "value": value,
        }
        metadata["reportMetadata"]["reportFilters"].append(filter_dict)


def update_filter(index, key, value, metadata):
    """
    Auxiliary function to update an arbitrary
    dictionary in a list of dicts.
    """
    metadata["reportMetadata"]["reportFilters"][index][key] = value


def increment_logical_filter(metadata):
    """
    Auxiliary function to increment the current
    logical filter. This is needed because we add
    an additional filter and, if there is one,
    we need to add it into the filter logic, otherwise
    an error is thrown.
    """
    logic = metadata["reportMetadata"]["reportBooleanFilter"]
    if logic:
        # get last number, for example, get 3 in '(1 AND (2 OR 3))'
        last_number = re.search(r"(\d+)\)*$", logic).group(1)
        # turn filter into '(1 AND (2 OR 3)) AND 4'
        new_logic = logic + " AND {}".format(int(last_number) + 1)

        metadata["reportMetadata"]["reportBooleanFilter"] = new_logic


def set_logic(logic, metadata):
    """
    Auxiliary function to update the logical
    filter value.
    """
    metadata["reportMetadata"]["reportBooleanFilter"] = logic


def set_period(start, end, column, metadata):
    date_filter = metadata["reportMetadata"]["standardDateFilter"]
    date_filter["durationValue"] = "CUSTOM"
    if column:
        date_filter["column"] = parsers.get_columns_labels(metadata)[column]
    if start:
        date_filter["startDate"] = parser.parse(start, dayfirst=True).strftime(
            "%Y-%m-%d"
        )
    if end:
        date_filter["endDate"] = parser.parse(end, dayfirst=True).strftime("%Y-%m-%d")
