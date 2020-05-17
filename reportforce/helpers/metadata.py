import re
import itertools

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
            value = self.format_value(value, api_name)

            self.report_filters.append(
                {"column": api_name, "operator": operator, "value": value}
            )

    def format_value(self, value, column):
        dtype = self.get_column_dtype(column)

        if dtype in ["datetime", "date", "time"]:
            if utils.is_iterable(value):
                return ",".join(map(self.format_date, value))
            else:
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
            new_logic = self._increment_boolean_filter(logic)
            self.boolean_filter = new_logic

    @staticmethod
    def _increment_boolean_filter(logic):
        last_number = re.sub(r"[()]", "", logic).split()[-1]
        new_logic = logic + f" AND {int(last_number) + 1}"
        return new_logic

    @property
    def date_filter(self):
        return self.report_metadata["standardDateFilter"]

    @property
    def date_start(self):
        return self.date_filter["startDate"]

    @date_start.setter
    def date_start(self, date_string):
        self.date_filter["startDate"] = self.format_date(date_string)

    @property
    def date_end(self):
        return self.date_filter["endDate"]

    @date_end.setter
    def date_end(self, date_string):
        self.date_filter["endDate"] = self.format_date(date_string)

    @property
    def date_column(self):
        return self.date_filter["column"]

    @date_column.setter
    def date_column(self, column):
        self.date_filter["column"] = self.get_column_api_name(column)

    @property
    def date_duration(self):
        return self.date_filter["durationValue"]

    @date_duration.setter
    def date_duration(self, duration):
        self.date_filter["durationValue"] = duration

    def ignore_date_filter(self):
        self.date_duration = "CUSTOM"
        self.date_start = None
        self.date_end = None

    def set_date_duration(self, duration):
        start, end, duration = self.get_duration_info(duration)

        self.date_duration = duration
        self.date_start = start
        self.date_end = end

    @property
    def detail_column_info(self):
        return self.extended_metadata["detailColumnInfo"].items()

    @property
    def aggregate_column_info(self):
        return self.extended_metadata["aggregateColumnInfo"].items()

    @property
    def all_available_columns(self):
        return itertools.chain(
            *(
                obj["columns"].items()
                for obj in self["reportTypeMetadata"]["categories"]
            )
        )

    @property
    def all_columns_info(self):
        return itertools.chain(
            self.detail_column_info,
            self.aggregate_column_info,
            self.all_available_columns,
        )

    def get_column_info_by_api_name(self, target, info):
        for api_name, infos in self.all_columns_info:
            if api_name == target:
                return infos[info]

    def get_column_info_by_label(self, target, info):
        for api_name, infos in self.all_columns_info:
            if infos["label"] == target:
                return api_name if info == "apiName" else infos[info]

    def get_column_label(self, column):
        return self.get_column_info_by_api_name(column, "label")

    def get_column_dtype(self, column):
        return self.get_column_info_by_api_name(column, "dataType")

    def get_column_api_name(self, column):
        return self.get_column_info_by_label(column, "apiName")

    def get_columns_labels(self):
        return [
            self.get_column_label(column) for column, _ in self.get_included_columns()
        ]

    def get_columns_dtypes(self):
        return [
            self.get_column_dtype(column) for column, _ in self.get_included_columns()
        ]

    def get_included_columns(self):
        return (
            self.aggregate_column_info
            if self.report_format == "MATRIX"
            else self.detail_column_info
        )

    def get_groupings_labels(self):
        return [
            group["label"]
            for group in self.extended_metadata["groupingColumnInfo"].values()
        ]

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
