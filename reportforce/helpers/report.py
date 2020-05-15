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

    def map_columns_to_info(self):
        """Map the column label to information like its type and API name."""
        return {
            info["label"]: {"dtype": info["dataType"], "api_name": column}
            for column, info in self.get_columns_info().items()
        }

    def get_columns_info(self):
        """Get information about columns. For matrices, about aggregates."""
        if self.format == "MATRIX":
            return self.extended_metadata["aggregateColumnInfo"]
        return self.extended_metadata["detailColumnInfo"]

    def get_columns_dtypes(self):
        return [info["dtype"] for info in self.map_columns_to_info().values()]

    def get_column_dtype(self, column):
        return self.map_columns_to_info()[column]["dtype"]

    def get_columns_labels(self):
        return (
            list(self.map_columns_to_info().keys())
            if self.format != "MATRIX"
            else self.get_matrix_columns()
        )

    def get_matrix_columns(self):
        groupings_across = self["groupingsAcross"]["groupings"]
        groups = parsers.get_groups(groupings_across)

        aggregates = list(self.map_columns_to_info().keys())

        groups_and_aggs = []
        for group in groups:
            for agg in aggregates:
                groups_and_aggs.append((agg,) + group)

        if groups_and_aggs:
            groups_labels = [""] + self.get_groupings_across_labels()
            return pd.MultiIndex.from_tuples(groups_and_aggs, names=groups_labels)

    def get_groupings_labels(self, groupings):
        groups = [group["name"] for group in groupings]
        group_info = self.extended_metadata["groupingColumnInfo"]

        return [group_info[group]["label"] for group in groups]

    def get_groupings_down_labels(self):
        return self.get_groupings_labels(self.report_metadata["groupingsDown"])

    def get_groupings_across_labels(self):
        return self.get_groupings_labels(self.report_metadata["groupingsAcross"])
