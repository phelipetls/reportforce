import pandas as pd

from ..helpers import parsers
from ..helpers.metadata import Metadata


class Report(Metadata, dict):
    @property
    def format(self):
        return self.keys()

    @property
    def all_data(self):
        return self["allData"]

    @property
    def dtypes(self):
        return [info["dtype"] for info in self._columns_info.values()]

    def get_column_dtype(self, column):
        return self._get_columns_info[column]["dtype"]

    @property
    def _columns_info(self):
        return {
            info["label"]: {"dtype": info["dataType"], "api_name": column}
            for column, info in self._get_columns_infos().items()
        }

    def _get_columns_infos(self):
        if self.format == "MATRIX":
            return self.extended_metadata["aggregateColumnInfo"]
        return self.extended_metadata["detailColumnInfo"]


class Tabular(Report):
    @property
    def rows(self):
        return self["factMap"]["T!T"]["rows"]

    def parse(self):
        return [
            [parsers.get_value(cell, dtype) for cell in row["dataCells"]]
            for row, dtype in zip(self.rows, self.dtypes)
        ]

    def to_dataframe(self):
        return pd.DataFrame(self.parse())
