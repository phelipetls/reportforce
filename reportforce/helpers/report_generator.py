import pandas as pd

from .. import helpers

base_url = "https://{}/services/data/v{}/analytics/reports/{}"


def report_generator(get_report):
    def generator(report_id, id_column, metadata, session):
        url = base_url.format(session.instance_url, session.version, report_id)

        report, report_cells, indices = get_report(url, metadata, session)

        if len(report["factMap"]) == 1:
            return pd.DataFrame()

        columns_labels = helpers.parsers.get_column_labels(metadata)

        df = pd.DataFrame(report_cells, index=indices, columns=columns_labels)
        yield df

        if id_column:
            already_seen = ""
            helpers.filtering.set_filters([(id_column, "!=", already_seen)], metadata)
            helpers.filtering.increment_logical_filter(metadata)

            while not report["allData"]:
                # getting what is need to build the dataframe
                report, report_cells, indices = get_report(url, metadata, session)

                # helpers.filtering out already seen values
                if id_column:
                    already_seen += ",".join(df[id_column].values)
                    helpers.filtering.update_filter(-1, "value", already_seen, metadata)

                df = pd.DataFrame(report_cells, index=indices, columns=columns_labels)
                yield df

    return generator
