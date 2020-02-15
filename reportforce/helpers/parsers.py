import re
import itertools
import collections


def get_tabular_cells(report):
    factmap = report["factMap"]
    rows = factmap["T!T"]["rows"]
    cells = [[cell["label"] for cell in row["dataCells"]] for row in rows]
    return cells


def get_summary_cells(report):
    factmap = report["factMap"]
    cells = []
    cells_by_group = []

    n_groups = len(report["reportMetadata"]["groupingsDown"])
    pattern = r"\d_" * (n_groups - 1)

    groups = itertools.filterfalse(lambda x: not re.search(pattern, x), factmap)

    sort_func = lambda x: list(map(int, x.rstrip("!T").split("_")))
    for group in sorted(groups, key=sort_func):
        rows = factmap[group]["rows"]
        for row in rows:
            cells.append([cell["label"] for cell in row["dataCells"]])
        cells_by_group.append(len(rows))

    return cells, cells_by_group


def get_column_labels(metadata):
    columns_info = metadata["reportExtendedMetadata"]["detailColumnInfo"]
    return {info["label"]: column for column, info in columns_info.items()}


def get_matrix_cells(matrix):
    n_rows = len(matrix["reportMetadata"]["groupingsDown"])
    n_cols = len(matrix["reportMetadata"]["groupingsAcross"])

    values = []
    for key, value in sorted(matrix["factMap"].items()):
        row_groups, col_groups = key.split("!")
        row_condition = re.search(r"\d_?" * n_rows, row_groups)
        col_condition = re.search(r"\d_?" * n_cols, col_groups)
        if row_condition and col_condition:
            values.append(value["aggregates"][0]["label"])
    return values


def get_groups(groups):
    indices = []
    for group in groups:
        groups_values = get_groups_values([group], [])
        indices.extend(itertools.product(*groups_values))
    return indices


def get_groups_values(groups, L=[]):
    L.append([group["label"] for group in groups])
    for group in groups:
        if group["groupings"]:
            return get_groups_values(group["groupings"], L)
        else:
            return L
