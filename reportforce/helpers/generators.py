import functools
import pandas as pd

from ..helpers import parsers
from ..helpers.report_filters import (
    update_filter_value,
    set_filters,
    increment_logical_filter,
)

URL = "https://{}/services/data/v{}/analytics/reports/{}"


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
            already_seen = ""
            increment_logical_filter(metadata)
            set_filters([(id_column, "!=", already_seen)], metadata)

        while not report["allData"] and id_column:
            # filtering out already seen values for the next report
            column = df[id_column]
            already_seen += ",".join(column.values) + ","

            update_filter_value(
                index=-1, value=already_seen.strip(","), metadata=metadata
            )

            # getting what is needed to build the dataframe
            report, report_cells, indices = get_report(
                url, metadata, salesforce, **kwargs
            )

            df = pd.DataFrame(report_cells, index=indices, columns=columns)
            yield df

    @functools.wraps(get_report)
    def concat(*args, **kwargs):
        kwargs.setdefault("params", {"includeDetails": "true"})

        df = pd.concat(generator(*args, **kwargs))

        if not isinstance(df.index, pd.MultiIndex):
            df = df.reset_index(drop=True)

        return df

    return concat
