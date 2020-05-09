import functools
import pandas as pd

from ..helpers import parsers
from ..helpers.report_filters import (
    filter_by_sort,
    filter_id_column,
    update_id_column_filter,
    increment_logical_filter,
)


def report_generator(get_report):
    """Decorator function to yield reports (as a DataFrame)
    until the allData item of the response body is 'true',
    which eventually will be because we filter out already
    seen values of an specified identifier column.

    It then concatenates and returns all generated
    DataFrame.

    If an id_column is not provided or if the report is less
    than 2000 rows, then there is nothing that could be done.
    """

    def generator(report_id, id_column, metadata, salesforce, **kwargs):
        """Request reports until allData is true by filtering them iteratively."""
        url = salesforce.url + report_id

        report, report_cells, indices = get_report(url, metadata, salesforce, **kwargs)

        columns = parsers.get_columns(report)
        df = pd.DataFrame(report_cells, index=indices, columns=columns)
        yield df

        if not report["allData"] and id_column:
            filter_value = ""
            by_sort = filter_by_sort(df, id_column, metadata)

            filter_id_column(by_sort, id_column, metadata)

            increment_logical_filter(metadata)

        while not report["allData"] and id_column:
            column = df[id_column]

            filter_value = update_id_column_filter(
                filter_value, by_sort, column, metadata
            )

            report, report_cells, indices = get_report(
                url, metadata, salesforce, **kwargs
            )

            df = pd.DataFrame(report_cells, index=indices, columns=columns)
            yield df

    @functools.wraps(get_report)
    def report_concatenator(*args, **kwargs):
        kwargs.setdefault("params", {"includeDetails": "true"})

        df = pd.concat(generator(*args, **kwargs))

        if not isinstance(df.index, pd.MultiIndex):
            df = df.reset_index(drop=True)

        return df

    return report_concatenator
