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
    """Append each filter in a list of filter to report metadata."""
    for filter_ in filters:
        column, operator, value = filter_
        filter_dict = {
            "column": parsers.get_columns_labels(metadata)[column],
            "operator": operators_dict.get(operator),
            "value": value,
        }
        metadata["reportMetadata"]["reportFilters"].append(filter_dict)


def update_filter(index, key, value, metadata):
    """Update an arbitrary filter key-value pair in a list of filters."""
    metadata["reportMetadata"]["reportFilters"][index][key] = value


def increment_logical_filter(metadata):
    """Increment logical filter by an additional column.

    This is used to avoid an error being thrown when we
    filter by an identifier column without including it
    in the filter logic.
    """
    logic = metadata["reportMetadata"]["reportBooleanFilter"]
    if logic:
        # get last number, for example, get 3 in '(1 AND (2 OR 3))'
        last_number = re.search(r"(\d+)\)*$", logic).group(1)
        # turn filter into '(1 AND (2 OR 3)) AND 4'
        new_logic = logic + " AND {}".format(int(last_number) + 1)

        metadata["reportMetadata"]["reportBooleanFilter"] = new_logic


def set_logic(logic, metadata):
    """Set logical filter value."""
    metadata["reportMetadata"]["reportBooleanFilter"] = logic


def set_period(start, end, column, metadata):
    """Set date-related filters parameters."""
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
