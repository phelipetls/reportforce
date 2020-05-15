import pandas as pd

from ..helpers import parsers
from ..helpers.report import Report


class Tabular(Report):
    @property
    def rows(self):
        return self["factMap"]["T!T"]["rows"]

    def get_cells(self):
        dtypes = self.get_columns_dtypes()

        return [
            [
                parsers.get_value(cell, dtype)
                for cell, dtype in zip(row["dataCells"], dtypes)
            ]
            for row in self.rows
        ]

    def to_dataframe(self):
        cells = self.get_cells()
        columns = self.get_columns_labels()

        return pd.DataFrame(cells, columns=columns)
