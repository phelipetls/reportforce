def get_cells(report):
    factmap = report["factMap"]
    # retrieving records
    rows = factmap["T!T"]["rows"]
    cells = [[cell["label"] for cell in row["dataCells"]] for row in rows]
    return cells


def get_column_labels_dict(metadata):
    columns_info = metadata["reportExtendedMetadata"]["detailColumnInfo"]
    return {info["label"]: column for column, info in columns_info.items()}
