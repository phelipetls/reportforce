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
                {"column": api_name, "operator": operator, "value": value}
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
        if value is not None:
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
            new_logic = self._add_new_filter_to_boolean_filter(logic)
            self.boolean_filter = new_logic

    @staticmethod
    def _add_new_filter_to_boolean_filter(logic):
        last_number = re.sub(r"[()]", "", logic).split()[-1]
        new_logic = logic + f" AND {int(last_number) + 1}"
        return new_logic

    @property
    def date_filter(self):
        return self.report_metadata["standardDateFilter"]

    @property
    def date_start(self):
        return self.report_metadata["standardDateFilter"]["startDate"]

    @date_start.setter
    def date_start(self, date_string):
        self.report_metadata["standardDateFilter"]["startDate"] = self.format_date(
            date_string
        )

    @property
    def date_end(self):
        return self.report_metadata["standardDateFilter"]["endDate"]

    @date_end.setter
    def date_end(self, date_string):
        self.report_metadata["standardDateFilter"]["endDate"] = self.format_date(
            date_string
        )

    @property
    def date_column(self):
        return self.report_metadata["standardDateFilter"]["column"]

    @date_column.setter
    def date_column(self, column):
        self.report_metadata["standardDateFilter"]["column"] = self.get_column_api_name(
            column
        )

    @property
    def date_duration(self):
        return self.report_metadata["standardDateFilter"]["durationValue"]

    @date_duration.setter
    def date_duration(self, duration):
        self.report_metadata["standardDateFilter"][
            "durationValue"
        ] = duration

    def ignore_date_filter(self):
        self.date_duration = "CUSTOM"
        self.date_start = None
        self.date_end = None

    def set_date_duration(self, duration):
        start, end, duration = self.get_duration_info(duration)

        self.date_duration = duration
        self.date_start = start
        self.date_end = end

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
        try:
            return self.map_columns_to_info()[column]["dtype"]
        except KeyError:
            return self.get_all_columns_info()[column]["dtype"]

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

    def get_duration_info(self, duration):
        return self.get_date_filter_durations_groups()[duration].values()

    def get_date_filter_durations_groups(self):
        date_filter_durations_groups = {}

        for group in self["reportTypeMetadata"]["standardDateFilterDurationGroups"]:
            date_filter_durations_groups.update(
                {
                    duration["label"]: {
                        "start": duration["startDate"],
                        "end": duration["endDate"],
                        "value": duration["value"],
                    }
                    for duration in group["standardDateFilterDurations"]
                }
            )

        return date_filter_durations_groups
