import re

from dateutil.parser import parse


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

            self.report_filters.append(
                {
                    "column": self.get_column_api_name(column),
                    "operator": self.operators.get(operator),
                    "value": value,
                }
            )

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

        column = self.get_column_api_name(column)
        start = parse(start, dayfirst=True).isoformat()[:10]
        end = parse(end, dayfirst=True).isoformat()[:10]

        self.report_metadata["standardDateFilter"]["durationValue"] = "CUSTOM"
        self.report_metadata["standardDateFilter"]["startDate"] = start
        self.report_metadata["standardDateFilter"]["endDate"] = end
        self.report_metadata["standardDateFilter"]["column"] = column

    def get_columns_labels(self):
        return list(self.columns_info.keys())

    def get_column_api_name(self, column):
        return self.columns_info[column]["api_name"]

    def get_column_dtype(self, column):
        return self.columns_info[column]["dtype"]

    def get_columns_dtypes(self):
        return [info["dtype"] for info in self.columns_info.values()]

    def get_groupings_labels(self):
        return [
            group["label"]
            for group in self.extended_metadata["groupingColumnInfo"].values()
        ]
