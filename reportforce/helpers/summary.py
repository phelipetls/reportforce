import re
import itertools
import pandas as pd

from distutils.version import LooseVersion

from ..helpers import parsers
from ..helpers.report import Report


class Summary(Report):
    def get_cells(self):
        factmap = self["factMap"]

        cells = []
        group_frequency = []

        # pattern to filter out sub/grandtotals
        n_groups = len(self.report_metadata["groupingsDown"])
        pattern = r"_".join(["[0-9]"] * n_groups)

        # filter out all keys that are sub/grandtotals
        groups = [group for group in factmap if re.search(pattern, group)]
        dtypes = self.get_columns_dtypes()

        for group in sorted(groups, key=LooseVersion):
            rows = factmap[group]["rows"]
            for row in rows:
                data_cells = row["dataCells"]
                cells.append(
                    [
                        parsers.get_value(cell, dtype)
                        for cell, dtype in zip(data_cells, dtypes)
                    ]
                )
            group_frequency.append(len(rows))

        return cells, group_frequency

    def get_index(self, group_frequency):
        groups = parsers.get_groups(self["groupingsDown"]["groupings"])
        groups_frequency_pairs = zip(groups, group_frequency)

        repeated_groups = itertools.chain.from_iterable(
            itertools.starmap(itertools.repeat, groups_frequency_pairs)
        )

        names = self.get_groupings_down_labels()
        return pd.MultiIndex.from_tuples(repeated_groups, names=names)

    def to_dataframe(self):
        cells, group_frequency = self.get_cells()
        index = self.get_index(group_frequency)
        columns = self.get_columns_labels()

        return pd.DataFrame(cells, columns=columns, index=index)
