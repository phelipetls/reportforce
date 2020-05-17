import itertools
import pandas as pd

number_types = ["double", "percent", "int"]
date_types = ["datetime", "date", "time"]


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


def get_groups(groups):
    """Iterate through a list of groupings to
    get the cartesian product of their values.

    For example, given this list of groupings:

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
    all_groups = []
    for group in groups:
        groups_labels = get_groups_labels([group], [])
        all_groups.extend(itertools.product(*groups_labels))
    return all_groups


def get_groups_labels(groups, groupings_labels=[]):
    """Recursively extract the labels for each
    group, for every level of nesting.

    Examples
    --------
    >>> get_groups_labels(g)
    [['grouping1'], ['grouping2'], ['grouping3_1', 'grouping3_2'], ['grouping4_1', 'grouping4_1']]
    """
    labels = []
    nested_groupings = []

    for group in groups:
        labels.append(group["label"])
        nested_groupings.extend(group["groupings"])

    groupings_labels.append(labels)
    if nested_groupings:
        get_groups_labels(nested_groupings, groupings_labels)

    return groupings_labels
