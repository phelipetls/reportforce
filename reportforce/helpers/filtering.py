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


def set_logic(logic, metadata):
    metadata["reportBooleanFilter"] = logic


def set_period(start, end, metadata):
    date_filter = metadata["reportMetadata"]["standardDateFilter"]
    date_filter["startDate"] = parser.parse(start).strftime("%Y-%m-%d")
    date_filter["endDate"] = parser.parse(end).strftime("%Y-%m-%d")
    date_filter["durationValue"] = "CUSTOM"
