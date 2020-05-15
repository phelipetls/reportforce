import re
import numpy as np
import pandas as pd

from distutils.version import LooseVersion

from reportforce.helpers import parsers
from reportforce.helpers.report import Report


class Matrix(Report):
    def to_dataframe(self):
        cells = np.array(self.get_cells())

        if cells.size == 0:
            return pd.DataFrame()

        columns = self.get_columns_labels()
        index = self.get_index()

        cells.shape = (len(index), len(columns))

        return pd.DataFrame(cells, columns=columns, index=index)

    def get_cells(self):
        factmap = self["factMap"]

        n_rows = len(self.report_metadata["groupingsDown"])
        n_cols = len(self.report_metadata["groupingsAcross"])

        # patterns to filter out sub/grandtotals
        row_pattern = r"_".join(["[0-9]+"] * n_rows)
        col_pattern = r"_".join(["[0-9]+"] * n_cols)
        pattern = f"{row_pattern}!{col_pattern}"

        groups = [group for group in factmap if re.search(pattern, group)]
        dtypes = self.get_columns_dtypes()

        cells = []
        for group in sorted(groups, key=LooseVersion):
            aggregates = factmap[group]["aggregates"]
            for agg, dtype in zip(aggregates, dtypes):
                value = parsers.get_value(agg, dtype)
                cells.append(value)

        return cells

    def get_index(self):
        groupings = self["groupingsDown"]["groupings"]
        names = self.get_groupings_down_labels()
        return pd.MultiIndex.from_tuples(parsers.get_groups(groupings), names=names)
