import functools
import pandas as pd

from ..helpers import parsers
from ..helpers.report_filters import (
    filter_id_column,
    update_filter_out,
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

    @functools.wraps(get_report)
    def report_concatenator(*args, **kwargs):
        kwargs.setdefault("params", {"includeDetails": "true"})

        df = pd.concat(generator(*args, **kwargs))

        if not isinstance(df.index, pd.MultiIndex):
            df = df.reset_index(drop=True)

        return df

    return report_concatenator


def generator(report_id, id_column, metadata, salesforce, **kwargs):
    """Request reports until allData is true by filtering them iteratively."""
    url = salesforce.url + report_id

    report, report_cells, indices = get_report(url, metadata, salesforce, **kwargs)

    columns = parsers.get_columns(report)

    df = pd.DataFrame(report_cells, index=indices, columns=columns)
    yield df

    if not report["allData"] and id_column:
        filter_value = ""

        all_unique = len(df[id_column].unique()) == 2000
        filter_id_column(all_unique, id_column, metadata)

        increment_logical_filter(metadata)

    while not report["allData"] and id_column:
        # filtering out already seen values for the next report
        column = df[id_column]

        filter_value = update_filter_out(filter_value, all_unique, column, metadata)

        # getting what is needed to build the dataframe
        report, report_cells, indices = get_report(
            url, metadata, salesforce, **kwargs
        )

        df = pd.DataFrame(report_cells, index=indices, columns=columns)
        yield df
