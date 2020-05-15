import re

from dateutil.parser import parse
from reportforce.helpers import utils


class Metadata(dict):
    @property
    def report_metadata(self):
        return self["reportMetadata"]

    @property
    def extended_metadata(self):
        return self["reportExtendedMetadata"]

    @property
    def report_format(self):
        return self.report_metadata["reportFormat"]

    @property
    def report_filters(self):
        return self.report_metadata["reportFilters"]

    @report_filters.setter
    def report_filters(self, params):
        for param in params:
            column, operator, value = param

            api_name = self.get_column_api_name(column)
            operator = self.get_operator(operator)
            value = self.format_value(value, column)

            self.report_filters.append(
                {
                    "column": api_name,
                    "operator": operator,
                    "value": value,
                }
            )

    def format_value(self, value, column):
        dtype = self.get_column_dtype(column)

        if dtype in ["datetime", "date", "time"]:
            return self.format_date(value)
        elif utils.is_iterable(value):
            return ",".join(map(utils.surround_with_quotes, value))
        else:
            return utils.surround_with_quotes(value)

    @staticmethod
    def format_date(value):
        return parse(value, dayfirst=True).isoformat()

    operators = {
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

    def get_operator(self, operator):
        return self.operators.get(operator)

    @property
    def boolean_filter(self):
        return self.report_metadata["reportBooleanFilter"]

    @boolean_filter.setter
    def boolean_filter(self, logic):
        self.report_metadata["reportBooleanFilter"] = logic

    def increment_boolean_filter(self):
        logic = self.boolean_filter
        if logic:
            last_number = re.sub(r"[()]", "", logic).split()[-1]
            new_logic = logic + f" AND {int(last_number) + 1}"
            self.boolean_filter = new_logic

    @property
    def date_filter(self):
        return self.report_metadata["standardDateFilter"]

    @date_filter.setter
    def date_filter(self, params):
        start, end, column = params

        self.report_metadata["standardDateFilter"]["durationValue"] = "CUSTOM"

        if start:
            start = self.format_date(start)
            self.report_metadata["standardDateFilter"]["startDate"] = start

        if end:
            end = self.format_date(end)
            self.report_metadata["standardDateFilter"]["endDate"] = end

        if column:
            column = self.get_column_api_name(column)
            self.report_metadata["standardDateFilter"]["column"] = column

    def map_columns_to_info(self):
        return {
            info["label"]: {"dtype": info["dataType"], "api_name": column}
            for column, info in self.get_columns_info().items()
        }

    def get_columns_info(self):
        if self.report_format == "MATRIX":
            return self.extended_metadata["aggregateColumnInfo"]
        return self.extended_metadata["detailColumnInfo"]

    def get_columns_labels(self):
        return list(self.map_columns_to_info().keys())

    def get_columns_dtypes(self):
        return [info["dtype"] for info in self.map_columns_to_info().values()]

    def get_column_dtype(self, column):
        return self.map_columns_to_info()[column]["dtype"]

    def get_column_api_name(self, column):
        try:
            return self.map_columns_to_info()[column]["api_name"]
        except KeyError:
            return self.get_all_columns_info()[column]["api_name"]

    def get_groupings_labels(self):
        return [
            group["label"]
            for group in self.extended_metadata["groupingColumnInfo"].values()
        ]

    def get_all_columns_info(self):
        all_objects = self["reportTypeMetadata"]["categories"]

        all_columns = {}
        for obj in all_objects:
            all_columns.update(
                {
                    info["label"]: {"dtype": info["dataType"], "api_name": api_name}
                    for api_name, info in obj["columns"].items()
                }
            )

        return all_columns
