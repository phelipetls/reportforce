import re
import itertools
import pandas as pd

from distutils.version import LooseVersion


def get_tabular_cells(report):
    """
    Auxiliary function to get all cells
    from tabular report.
    """
    rows = report["factMap"]["T!T"]["rows"]
    return [[cell["label"] for cell in row["dataCells"]] for row in rows]


def get_matrix_cells(matrix):
    """
    Auxiliary function to get all cells
    from a matrix report.
    """
    factmap = matrix["factMap"]

    n_rows = len(matrix["reportMetadata"]["groupingsDown"])
    n_cols = len(matrix["reportMetadata"]["groupingsAcross"])

    # patterns to filter out sub/grandtotals
    row_pattern = r"_".join(["[0-9]+"] * n_rows)
    col_pattern = r"_".join(["[0-9]+"] * n_cols)
    pattern = row_pattern + "!" + col_pattern

    groups = [group for group in factmap if re.search(row_pattern + "!" + col_pattern, group)]

    cells = []
    for group in sorted(groups, key=LooseVersion):
        cells.extend([agg["label"] for agg in factmap[group]["aggregates"]])

    return cells


def get_summary_cells(summary):
    """
    Auxiliary function to get all cells
    from a summary report.
    """
    factmap = summary["factMap"]
    cells = []
    cells_by_group = []

    # pattern to filter out sub/grandtotals
    n_groups = len(summary["reportMetadata"]["groupingsDown"])
    pattern = r"_".join(["[0-9]"] * n_groups)

    # filter out all keys not matching the pattern
    groups = [group for group in factmap if re.search(pattern, group)]

    for group in sorted(groups, key=LooseVersion):
        rows = factmap[group]["rows"]
        for row in rows:
            cells.append([cell["label"] for cell in row["dataCells"]])
        cells_by_group.append(len(rows))

    return cells, cells_by_group


def get_summary_indices(summary, cells_by_group):
    """
    Auxiliary function to get summary report
    MultiIndex.
    """
    groups = get_groups(summary["groupingsDown"]["groupings"])
    groups_frequency_pairs = zip(groups, cells_by_group)

    repeated_groups = itertools.chain.from_iterable(
        itertools.starmap(itertools.repeat, groups_frequency_pairs)
    )

    return pd.MultiIndex.from_tuples(repeated_groups)


dtypes = {
    "datetime": "datetime64",
    "date": "datetime64",
    "time": "datetime64",
    "string": "string",
    "boolean": "boolean",
    "currency": "currency",
    "percent": "percent",
    "picklist": "string",
    "int": "int"
}


def get_columns_types(metadata):
    if metadata["reportMetadata"]["reportFormat"] == "MATRIX":
        columns_info = metadata["reportExtendedMetadata"]["groupingColumnInfo"]
    else:
        columns_info = metadata["reportExtendedMetadata"]["detailColumnInfo"]
    return [dtypes.get(info["dataType"], "object") for info in columns_info.values()]


def get_column_labels(report):
    """
    Auxiliary function to get a dict that maps a column label (which is shown
    in the browser) to its api name (which is only internal).

    The api name is the one that should be used in the request body.
    """
    if report["reportMetadata"]["reportFormat"] == "MATRIX":
        columns_info = report["reportExtendedMetadata"]["groupingColumnInfo"]
    else:
        columns_info = report["reportExtendedMetadata"]["detailColumnInfo"]
    return {info["label"]: column for column, info in columns_info.items()}


def get_columns(report):
    if report["reportMetadata"]["reportFormat"] == "MATRIX":
        groupings_across = report["groupingsAcross"]["groupings"]

        aggregate_info = report["reportExtendedMetadata"]["aggregateColumnInfo"]
        aggs = [agg["label"] for agg in aggregate_info.values()]

        column_groups = get_groups(groupings_across)

        multi_columns = []
        for col in column_groups:
            for agg in aggs:
                multi_columns.append((agg,) + col)

        return pd.MultiIndex.from_tuples(multi_columns)
    else:
        return get_column_labels(report)


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
