import re

from dateutil import parser
from reportforce.helpers import parsers

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


def filter_id_column(all_unique, id_column, metadata):
    if all_unique:
        set_sort_by(id_column, "asc", metadata)
        set_filters([(id_column, ">", "")], metadata)
    else:
        set_filters([(id_column, "!=", "")], metadata)


def update_filter_out(filter_value, all_unique, id_column, metadata):
    if all_unique:
        filter_value = id_column.iloc[-1]
    else:
        filter_value += "," + id_column.str.cat(sep=',', na_rep='-') + ","
        filter_value = filter_value.strip(",")

    update_filter_value(filter_value, metadata)

    return filter_value


def set_filters(filters, metadata):
    """Append each filter in a list of filter to report metadata."""
    for f in filters:
        column, operator, value = f
        filter_dict = {
            "column": parsers.get_column_api_name(column, metadata),
            "operator": operators_dict.get(operator),
            "value": value,
        }
        metadata["reportMetadata"]["reportFilters"].append(filter_dict)


def update_filter_value(value, metadata):
    """Update the value of last filter."""
    metadata["reportMetadata"]["reportFilters"][-1]["value"] = value


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
        date_filter["column"] = parsers.get_column_api_name(column, metadata)
    if start:
        date_filter["startDate"] = parser.parse(start, dayfirst=True).strftime(
            "%Y-%m-%d"
        )
    if end:
        date_filter["endDate"] = parser.parse(end, dayfirst=True).strftime("%Y-%m-%d")


def set_sort_by(sort_column, orientation, metadata):
    sort_column = parsers.get_column_api_name(sort_column, metadata)

    if re.match(r"^(a|de)sc$", orientation, flags=re.IGNORECASE):
        sort_order = orientation.title()
    else:
        raise ValueError(
            "Orientation should be either 'asc' or 'desc', not '{}'".format(orientation)
        )

    sort_by_dict = {"sortColumn": sort_column, "sortOrder": sort_order}
    metadata["reportMetadata"]["sortBy"] = sort_by_dict
