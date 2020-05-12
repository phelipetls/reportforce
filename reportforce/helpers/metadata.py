import copy

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

    @property
    def boolean_filter(self):
        return self.report_metadata["reportBooleanFilter"]

    @property
    def std_date_filter(self):
        return self.report_metadata["standardDateFilter"]

    @property
    def sort_by(self):
        return self.report_metadata["sortBy"]

    @property
    def groupings_down(self):
        return self.report_metadata["groupingsDown"]

    @property
    def groupings_across(self):
        return self.report_metadata["groupingsAcross"]

    def _get_infos(self):
        if self.report_format == "MATRIX":
            return self.extended_metadata["aggregateColumnInfo"]
        return self.extended_metadata["detailColumnInfo"]

    @property
    def columns_info(self):
        infos = self._get_infos()

        return {
            info["label"]: {"dtype": info["dataType"], "api_name": column}
            for column, info in infos.items()
        }

    def get_columns_labels(self):
        return list(self.columns_info.keys())

    def get_column_api_name(self, column):
        return self.columns_info[column]["api_name"]

    def get_columns_dtypes(self):
        return [info["dtype"] for info in self.columns_info.values()]

    def get_column_dtype(self, column):
        return self.columns_info[column]["dtype"]

    def get_groupings_labels(self):
        return [
            group["label"]
            for group in self.extended_metadata["groupingColumnInfo"].values()
        ]
