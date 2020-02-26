import re
import itertools
import pandas as pd

from distutils.version import LooseVersion

numbers = ["double", "percent", "int"]
dates = ["datetime", "date", "time"]


def get_value(cell, dtype):
    """ Auxiliary function to get cell value according to data type. """
    if dtype in numbers:
        return cell["value"]

    elif dtype in dates:
        return pd.Timestamp(cell["value"])

    elif dtype == "currency":
        try:
            return cell["value"]["amount"]
        except TypeError:
            return cell["value"]

    return cell["label"]


def get_tabular_cells(report):
    """ Auxiliary function to get all cells from tabular report. """
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
    """ Auxiliary function to get all cells from a matrix report. """
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
    """ Auxiliary function to get all cells from a summary report. """
    factmap = summary["factMap"]
    cells = []
    cells_by_group = []

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
        cells_by_group.append(len(rows))

    return cells, cells_by_group


def get_summary_indices(summary, cells_by_group):
    """ Auxiliary function to get summary report MultiIndex. """
    groups = get_groups(summary["groupingsDown"]["groupings"])
    groups_frequency_pairs = zip(groups, cells_by_group)

    repeated_groups = itertools.chain.from_iterable(
        itertools.starmap(itertools.repeat, groups_frequency_pairs)
    )

    names = get_groupings_labels(summary, "groupingsDown")

    return pd.MultiIndex.from_tuples(repeated_groups, names=names)


def get_columns_dtypes(report):
    """Get columns types"""
    report_format = report["reportMetadata"]["reportFormat"]

    if report_format == "MATRIX":
        info = report["reportExtendedMetadata"]["aggregateColumnInfo"]
        aggregates = report["reportMetadata"]["aggregates"]
        return [info[col]["dataType"] for col in aggregates]

    info = report["reportExtendedMetadata"]["detailColumnInfo"]
    columns = report["reportMetadata"]["detailColumns"]
    return [info[col]["dataType"] for col in columns]


def get_groupings_labels(report, key):
    """Get groupings labels"""
    groupings_metadata = report["reportExtendedMetadata"]["groupingColumnInfo"]
    groups_names = [group["name"] for group in report["reportMetadata"][key]]

    groups_labels = [groupings_metadata[name]["label"] for name in groups_names]
    return groups_labels


def get_columns_labels(report):
    """
    Auxiliary function to get a dict that maps a column label (which is shown
    in the browser) to its API name (which is only internal).

    The API name is the one that should be used in the request body.

    This is used to get the corresping label of a given column API name.
    """
    if report["reportMetadata"]["reportFormat"] == "MATRIX":
        columns_info = report["reportExtendedMetadata"]["groupingColumnInfo"]
    else:
        columns_info = report["reportExtendedMetadata"]["detailColumnInfo"]
    return {info["label"]: column for column, info in columns_info.items()}


def get_columns(report):
    """
    Auxiliary function to get a report columns labels in an appropriate
    format to be passed to the columns argument when creating a DataFrame.
    """

    if report["reportMetadata"]["reportFormat"] == "MATRIX":
        # get columns groups tuples
        groupings_across = report["groupingsAcross"]["groupings"]
        column_groups = get_groups(groupings_across)

        # get aggregate columns
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
    """
    Auxiliary function to iterate through a GroupingsDown or GroupingsAcross,
    which stores a list of groupings that may contain other groupings etc.

    It tries to return a list of tuples which results from the product of the
    values inside the group.
    """
    indices = []
    for group in groups:
        groups_values = get_groups_values([group], [])
        indices.extend(itertools.product(*groups_values))
    return indices


def get_groups_values(groups, L=[]):
    """
    Auxiliary function to recursively iterate through a grouping, which is a
    list of dictionary, extract theirs labels and append them into a list.

    The function stops when there are no more groupings inside a group.
    """
    L.append([group["label"] for group in groups])
    for group in groups:
        if group["groupings"]:
            return get_groups_values(group["groupings"], L)
        else:
            return L
