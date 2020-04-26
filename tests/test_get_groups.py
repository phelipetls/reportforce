from reportforce.helpers.parsers import get_groups_labels

groups = [
    {
        "groupings": [
            {
                "groupings": [
                    {
                        "groupings": [{"groupings": [], "label": "grouping4_1"}],
                        "label": "grouping3_1",
                    },
                    {
                        "groupings": [{"groupings": [], "label": "grouping4_2"}],
                        "label": "grouping3_2",
                    },
                ],
                "label": "grouping2",
            }
        ],
        "label": "grouping1",
    }
]


def test_get_groups_labels():
    test = get_groups_labels(groups)

    expected = [
        ["grouping1"],
        ["grouping2"],
        ["grouping3_1", "grouping3_2"],
        ["grouping4_1", "grouping4_2"],
    ]

    assert test == expected
