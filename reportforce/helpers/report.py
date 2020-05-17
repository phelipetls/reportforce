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

    def get_columns_info(self):
        return self.extended_metadata[
            "detailColumnInfo" if self.format != "MATRIX" else "aggregateColumnInfo"
        ]

    def get_column_dtype(self, label):
        for _, info in self.get_columns_info().items():
            if info["label"] == label:
                return info["dataType"]

    def get_columns_dtypes(self):
        return [info["dataType"] for _, info in self.get_columns_info().items()]

    def get_columns_labels(self):
        return [info["label"] for _, info in self.get_columns_info().items()]

    def get_groupings_labels(self, groupings):
        groups = [group["name"] for group in groupings]
        group_info = self.extended_metadata["groupingColumnInfo"]

        return [group_info[group]["label"] for group in groups]

    def get_groupings_down_labels(self):
        return self.get_groupings_labels(self.report_metadata["groupingsDown"])

    def get_groupings_across_labels(self):
        return self.get_groupings_labels(self.report_metadata["groupingsAcross"])
