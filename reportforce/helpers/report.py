import pandas as pd

from ..helpers import parsers


class Report(dict):
    @property
    def format(self):
        return self.report_metadata["reportFormat"]

    @property
    def all_data(self):
        return self["allData"]

    @property
    def report_metadata(self):
        return self["reportMetadata"]

    @property
    def extended_metadata(self):
        return self["reportExtendedMetadata"]

    def get_dtypes(self):
        return [info["dtype"] for info in self.get_column_info().values()]

    def get_column_dtype(self, column):
        return self.get_column_info()[column]["dtype"]

    def get_columns(self):
        if self.format != "MATRIX":
            return list(self.get_column_info().keys())
        return self.get_matrix_columns()

    def get_matrix_columns(self):
        groupings_across = self["groupingsAcross"]["groupings"]
        column_groups = parsers.get_groups(groupings_across)

        agg_info = self.extended_metadata["aggregateColumnInfo"]
        agg_labels = [
            agg_info[agg]["label"] for agg in self.report_metadata["aggregates"]
        ]

        multi_columns = []
        for col in column_groups:
            for label in agg_labels:
                multi_columns.append((label,) + col)

        if multi_columns:
            groups_labels = [""] + self.get_groupings_across_labels()
            return pd.MultiIndex.from_tuples(multi_columns, names=groups_labels)

    def get_column_info(self):
        return {
            info["label"]: {"dtype": info["dataType"], "api_name": column}
            for column, info in self._columns_info.items()
        }

    @property
    def _columns_info(self):
        if self.format == "MATRIX":
            return self.extended_metadata["aggregateColumnInfo"]
        return self.extended_metadata["detailColumnInfo"]

    def get_groupings_labels(self, groupings):
        groups = [group["name"] for group in groupings]
        group_info = self.extended_metadata["groupingColumnInfo"]

        return [group_info[group]["label"] for group in groups]

    def get_groupings_down_labels(self):
        return self.get_groupings_labels(self.report_metadata["groupingsDown"])

    def get_groupings_across_labels(self):
        return self.get_groupings_labels(self.report_metadata["groupingsAcross"])
