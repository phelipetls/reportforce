import itertools

def get_cells(report):
    factmap = report["factMap"]
    # retrieving records
    rows = factmap["T!T"]["rows"]
    cells = [[cell["label"] for cell in row["dataCells"]] for row in rows]
    return cells


def get_column_labels_dict(metadata):
    columns_info = metadata["reportExtendedMetadata"]["detailColumnInfo"]
    return {info["label"]: column for column, info in columns_info.items()}

def get_groups(groups):
    L = []
    for group in groups:
        L.extend(itertools.product(*get_group_values(group)))
    return L

def get_group_values(groups):
    L = [[groups["label"]]]
    next_groups = groups["groupings"]
    while next_groups:
        level = []
        for group in next_groups:
            level.append(group["label"])
        L.append([group["label"] for group in next_groups])
        next_groups = group["groupings"]
    return L
