import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportforce.helpers.parsers import get_groups_labels, get_groups

g = [
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


class TestGetGroups(unittest.TestCase):
    maxDiff = None

    def test_get_groups_labels(self):
        test = get_groups_labels(g)
        expected = [
            ["grouping1"],
            ["grouping2"],
            ["grouping3_1", "grouping3_2"],
            ["grouping4_1", "grouping4_2"],
        ]

        self.assertEqual(test, expected)


if __name__ == "__main__":
    unittest.main(failfast=True)
