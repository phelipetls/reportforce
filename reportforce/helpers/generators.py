import functools
import pandas as pd

from ..helpers import filters, parsers

URL = "https://{}/services/data/v{}/analytics/reports/{}"


def report_generator(get_report):
    """Decorator function to yield reports (as a DataFrame)
    until the allData item of the response body is 'true',
    which eventually will be because we filter out already
    seen values of a specified row-identifier column.

    It then concatenates and returns all generated
    DataFrame.

    If an id_column is not provided or if the report is less
    than 2000 rows, then there is nothing that could be done.
    """

    def generator(report_id, id_column, metadata, session, **kwargs):
        """Request reports until allData is true by filtering them iteratively."""
        url = URL.format(session.instance_url, session.version, report_id)

        report, report_cells, indices = get_report(url, metadata, session, **kwargs)

        columns = parsers.get_columns(report)

        df = pd.DataFrame(report_cells, index=indices, columns=columns)
        yield df

        if id_column:
            already_seen = ",".join(df[id_column].values)
            filters.set_filters([(id_column, "!=", already_seen)], metadata)

            filters.increment_logical_filter(metadata)

            while not report["allData"]:
                # getting what is needed to build the dataframe
                report, report_cells, indices = get_report(
                    url, metadata, session, **kwargs
                )

                df = pd.DataFrame(report_cells, index=indices, columns=columns)

                # filtering out already seen values
                already_seen += ",".join(df[id_column].values)
                filters.update_filter(-1, "value", already_seen, metadata)

                yield df

    @functools.wraps(get_report)
    def concat(*args, **kwargs):
        details = {"includeDetails": "true"}
        merge_params = kwargs.setdefault("params", {}).update(details)

        df = pd.concat(generator(*args, **kwargs))

        if not isinstance(df.index, pd.MultiIndex):
            df = df.reset_index(drop=True)

        return df

    return concat
