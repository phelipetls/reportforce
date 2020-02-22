import re
import itertools
import pandas as pd


def get_tabular_cells(report):
    """
    Auxiliary function to get all cells
    from tabular report.
    """
    factmap = report["factMap"]
    rows = factmap["T!T"]["rows"]
    cells = [[cell["label"] for cell in row["dataCells"]] for row in rows]
    return cells


def get_matrix_cells(matrix):
    """
    Auxiliary function to get all cells
    from a matrix report.

    This is much more complicated because we need
    to get the row and columns groups also.

    Besides, we also need to filter out the cells
    corresponding to subtotals and grand totals.

    It is also needed to sort the factMap keys to
    so that it first get the first row and all its
    columns, then jump to the next one.
    """
    factmap = matrix["factMap"]

    n_rows = len(matrix["reportMetadata"]["groupingsDown"])
    n_cols = len(matrix["reportMetadata"]["groupingsAcross"])

    # patterns to filter out subtotals and grandtotals
    # e.g, if there are 2 row groups, then get keys matching
    # the pattern [0-9]_[0-9], and if there is only
    # 1 column group, match the pattern [0-9]. this
    # will exclude any totals (denoted by "T") and also
    # subtotals, e.g. 0!0.
    row_pattern = r"_".join(["[0-9]"] * n_rows)
    col_pattern = r"_".join(["[0-9]"] * n_cols)

    # used to filter the factMap keys, e.g., to get
    # 0_0!0_1, 0_0!0_2, ..., 10_0!10_0, 10_0!10_1
    sort_func = lambda x: x.split("!")[0] + x.split("!")[1]  # noqa: E731

    values = []
    for group in sorted(factmap, key=sort_func):
        row_key, col_key = group.split("!")
        if re.search(row_pattern, row_key) and re.search(col_pattern, col_key):
            values.append(factmap[group]["aggregates"][0]["label"])
    return values


def get_summary_cells(report):
    """
    Auxiliary function to get all cells
    from a summary report.

    This is a lot similar to get_matrix_cells
    except that there aren't column groups.

    We still need to get the row_groups and filter
    out the sub/grandtotals.
    """
    factmap = report["factMap"]
    cells = []
    cells_by_group = []

    # pattern to filter out sub/grandtotals
    n_groups = len(report["reportMetadata"]["groupingsDown"])
    pattern = r"_".join(["[0-9]"] * n_groups)

    # filter out all keys not matching the pattern
    groups = itertools.filterfalse(lambda x: not re.search(pattern, x), factmap)

    sort_func = lambda x: [int(n) for n in x.rstrip("!T").split("_")]  # noqa: E731
    for group in sorted(groups, key=sort_func):
        rows = factmap[group]["rows"]
        for row in rows:
            cells.append([cell["label"] for cell in row["dataCells"]])
        cells_by_group.append(len(rows))

    return cells, cells_by_group


def get_column_labels(report):
    """
    Auxiliary function to get a dict that maps
    a column label (which is shown in the browser)
    to its api name (which is only internal).

    The api name is the one that should be
    used in the request body.
    """
    columns_info = report["reportExtendedMetadata"]["detailColumnInfo"]
    return {info["label"]: column for column, info in columns_info.items()}


def get_columns(report):
    if report["reportMetadata"]["reportFormat"] == "MATRIX":
        groupings_across = report["groupingsAcross"]["groupings"]
        multi_columns = get_groups(groupings_across)
        return pd.MultiIndex.from_tuples(multi_columns)
    else:
        return get_column_labels(report)


def get_groups(groups):
    """
    Auxiliary function to iterate through a
    GroupingsDown or GroupingsAcross, which
    stores a list of groupings that contains
    other groupings etc.

    It tries to return a list of tuples which
    is the product of the values inside the group.
    """
    indices = []
    for group in groups:
        groups_values = get_groups_values([group], [])
        indices.extend(itertools.product(*groups_values))
    return indices


def get_groups_values(groups, L=[]):
    """
    Auxiliary function to recursively iterate through
    a grouping, which is a list of dictionary, extract
    theirs labels and append them into a list.

    The function stops when there are no more groupings
    inside a group.
    """
    L.append([group["label"] for group in groups])
    for group in groups:
        if group["groupings"]:
            return get_groups_values(group["groupings"], L)
        else:
            return L
