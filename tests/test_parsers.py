import pandas as pd
from reportforce.helpers import parsers


class testGetValue:
    def test_get_currency(self):
        currency_cell = {"label": "$29", "value": 29}
        assert parsers.get_value(currency_cell, dtype="currency") == 29

    def test_get_currency_in_different_format(self):
        currency_cell = {"label": "$29", "value": {"amount": 29, "currency": None}}
        assert parsers.get_value(currency_cell, "currency") == 29

    def test_get_date(self):
        date_cell = {"label": "7/31/2015", "value": "2015-07-31"}
        assert parsers.get_value(date_cell, "date") == pd.Timestamp("2015-07-31")

    def test_get_any_other_value(self):
        others = {"label": "Qualitative", "value": "QUALITATIVE"}
        assert parsers.get_value(others, "picklist") == "Qualitative"


def test_get_groups_labels():
    assert parsers.get_groups_labels(groups) == [
        ["grouping1"],
        ["grouping2"],
        ["grouping3_1", "grouping3_2"],
        ["grouping4_1", "grouping4_2"],
    ]


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
