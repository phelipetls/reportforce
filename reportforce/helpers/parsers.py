import re
import itertools
import pandas as pd

from distutils.version import LooseVersion

number_types = ["double", "percent", "int"]
date_types = ["datetime", "date", "time"]


def get_report_format(metadata):
    return metadata["reportMetadata"]["reportFormat"]


def get_value(cell, dtype):
    """Get a cell value according to the column data type."""
    if dtype in number_types:
        return cell["value"]

    elif dtype in date_types:
        return pd.Timestamp(cell["value"])

    elif dtype == "currency":
        try:
            return cell["value"]["amount"]
        except TypeError:
            return cell["value"]

    return cell["label"]


def get_report_total(report):
    """Get a report grand total."""
    return report["factMap"]["T!T"]["aggregates"][0]["value"]


def get_tabular_cells(report):
    """Parse tabular report fact map"""
    rows = report["factMap"]["T!T"]["rows"]
    dtypes = get_columns_dtypes(report)

    cells = []
    for row in rows:
        L = []
        for cell, dtype in zip(row["dataCells"], dtypes):
            L.append(get_value(cell, dtype))
        cells.append(L)

    return cells


def get_matrix_cells(matrix):
    """Parse matrix report fact map."""
    factmap = matrix["factMap"]

    n_rows = len(matrix["reportMetadata"]["groupingsDown"])
    n_cols = len(matrix["reportMetadata"]["groupingsAcross"])

    # patterns to filter out sub/grandtotals
    row_pattern = r"_".join(["[0-9]+"] * n_rows)
    col_pattern = r"_".join(["[0-9]+"] * n_cols)
    pattern = row_pattern + "!" + col_pattern

    groups = [group for group in factmap if re.search(pattern, group)]

    dtypes = get_columns_dtypes(matrix)

    cells = []
    for group in sorted(groups, key=LooseVersion):
        aggregates = factmap[group]["aggregates"]
        for agg, dtype in zip(aggregates, dtypes):
            cells.append(get_value(agg, dtype))

    return cells


def get_summary_cells(summary):
    """Parse summary report fact map."""
    factmap = summary["factMap"]
    cells = []
    group_frequency = []

    # pattern to filter out sub/grandtotals
    n_groups = len(summary["reportMetadata"]["groupingsDown"])
    pattern = r"_".join(["[0-9]"] * n_groups)

    # filter out all keys not matching the pattern
    groups = [group for group in factmap if re.search(pattern, group)]
    dtypes = get_columns_dtypes(summary)

    for group in sorted(groups, key=LooseVersion):
        rows = factmap[group]["rows"]
        for row in rows:
            data_cells = row["dataCells"]
            cells.append(
                [get_value(cell, dtype) for cell, dtype in zip(data_cells, dtypes)]
            )
        group_frequency.append(len(rows))

    return cells, group_frequency


def get_summary_indices(summary, group_frequency):
    """Get summary report index (groups values for each line)."""
    groups = get_groups(summary["groupingsDown"]["groupings"])
    groups_frequency_pairs = zip(groups, group_frequency)

    repeated_groups = itertools.chain.from_iterable(
        itertools.starmap(itertools.repeat, groups_frequency_pairs)
    )

    names = get_groupings_labels(summary, "groupingsDown")
    return pd.MultiIndex.from_tuples(repeated_groups, names=names)


def get_columns_dtypes(report):
    """Get columns data types."""
    report_format = report["reportMetadata"]["reportFormat"]

    if report_format == "MATRIX":
        info = report["reportExtendedMetadata"]["aggregateColumnInfo"]
        aggregates = report["reportMetadata"]["aggregates"]
        return [info[col]["dataType"] for col in aggregates]

    info = report["reportExtendedMetadata"]["detailColumnInfo"]
    columns = report["reportMetadata"]["detailColumns"]

    return [info[col]["dataType"] for col in columns]


def get_groupings_labels(report, key):
    """Get row or column groupings labels, depending on key (groupingsDown/Across)."""
    groups_names = [group["name"] for group in report["reportMetadata"][key]]

    groupings_metadata = report["reportExtendedMetadata"]["groupingColumnInfo"]
    groups_labels = [groupings_metadata[name]["label"] for name in groups_names]

    return groups_labels


def get_columns_labels(report):
    """Get a dict that maps a column label (what you see in
    the browser) to its API name (used internally).

    The API name is the one that should be used in the
    request body.
    """
    columns_info = report["reportExtendedMetadata"]["detailColumnInfo"]
    return {info["label"]: column for column, info in columns_info.items()}


def get_columns(report):
    """Get report columns to pass to DataFrame constructor."""

    # for matrices, we actually need to get the columns groups labels
    if get_report_format(report) == "MATRIX":
        # get all columns groups
        groupings_across = report["groupingsAcross"]["groupings"]
        column_groups = get_groups(groupings_across)

        # get all used aggregates
        aggregates_info = report["reportExtendedMetadata"]["aggregateColumnInfo"]
        aggregates_labels = [
            aggregates_info[agg]["label"]
            for agg in report["reportMetadata"]["aggregates"]
        ]

        multi_columns = []
        for col in column_groups:  # append aggregates to groups
            for agg in aggregates_labels:
                multi_columns.append((agg,) + col)

        if multi_columns:
            groups_labels = [""] + get_groupings_labels(report, "groupingsAcross")
            return pd.MultiIndex.from_tuples(multi_columns, names=groups_labels)

    return get_columns_labels(report)


def get_groups(groups):
    """Iterate through a list of groupings to
    get the cartesian product of their values.

    For example, imagine this list of groupings:

    g = [
        {
            "groupings": [
                {
                    "groupings": [
                        {
                            "groupings": [
                                {
                                    "groupings": [],
                                    "label": "grouping4_1"
                                }
                                ],
                            "label": "grouping3_1",
                        },
                        {
                            "groupings": [
                                {
                                    "groupings": [],
                                    "label": "grouping4_1"
                                }
                                ],
                            "label": "grouping3_2",
                        },
                    ],
                    "label": "grouping2",
                }
            ],
            "label": "grouping1",
        }
    ]

    Our job is to extract the label of each group and put them
    in a list per level of nesting.

    Examples
    --------
    >>> get_groups(g)
    [('grouping1', 'grouping2', 'grouping3_1', 'grouping4_1'),
     ('grouping1', 'grouping2', 'grouping3_1', 'grouping4_1'),
     ('grouping1', 'grouping2', 'grouping3_2', 'grouping4_1'),
     ('grouping1', 'grouping2', 'grouping3_2', 'grouping4_1')]
    """
    indices = []
    for group in groups:
        groups_labels = get_groups_labels([group], [])
        indices.extend(itertools.product(*groups_labels))
    return indices


def get_groups_labels(groups, L=[]):
    """Recursively extract the labels for each
    group, for every level of nesting.

    Examples
    --------
    >>> get_groups_labels(g)
    [['grouping1'], ['grouping2'], ['grouping3_1', 'grouping3_2'], ['grouping4_1', 'grouping4_1']]
    """
    labels = []
    groupings = []

    for group in groups:
        labels.append(group["label"])
        groupings.extend(group["groupings"])
    else:
        L.append(labels)
        if groupings:
            get_groups_labels(groupings, L)
    return L
