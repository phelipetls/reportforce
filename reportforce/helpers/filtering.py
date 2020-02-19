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
    for filter_ in filters:
        column, operator, value = filter_
        filter_dict = {
            "column": parsers.get_column_labels(metadata)[column],
            "operator": operators_dict.get(operator),
            "value": value,
        }
        metadata["reportMetadata"]["reportFilters"].append(filter_dict)


def update_filter(index, key, value, metadata):
    metadata["reportMetadata"]["reportFilters"][index][key] = value


def increment_logical_filter(metadata):
    logic = metadata["reportMetadata"]["reportBooleanFilter"]
    if logic:
        last_number = re.search(r"(\d)\)*$", logic).group(1)
        new_logic = logic + " AND {}".format(int(last_number) + 1)
        metadata["reportMetadata"]["reportBooleanFilter"] = new_logic


def set_logic(logic, metadata):
    metadata["reportMetadata"]["reportBooleanFilter"] = logic


def set_period(start, end, column, metadata):
    date_filter = metadata["reportMetadata"]["standardDateFilter"]
    date_filter["durationValue"] = "CUSTOM"
    if column:
        date_filter["column"] = parsers.get_column_labels(metadata)[column]
    if start:
        date_filter["startDate"] = parser.parse(start, dayfirst=True).strftime(
            "%Y-%m-%d"
        )
    if end:
        date_filter["endDate"] = parser.parse(end, dayfirst=True).strftime("%Y-%m-%d")
