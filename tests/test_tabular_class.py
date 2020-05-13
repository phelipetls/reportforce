import pandas as pd

from reportforce.helpers.report import Tabular
from reportforce.helpers.metadata import Metadata

from fixtures_utils import read_json

REPORT = read_json("tabular.json")
METADATA = read_json("tabular_metadata.json")

tabular = Tabular(REPORT)


def test_tabular_dtypes():
    assert tabular.dtypes == [
        "string",
        "currency",
        "currency",
        "string",
        "percent",
        "string",
        "int",
        "datetime",
        "string",
        "string",
    ]


cells = [
    [
        "Acme - 200 Widgets",
        "$16,000.01",
        "$16,000.01",
        "Need estimate",
        "60%",
        "Q3-2015",
        "12",
        "7/31/2015",
        "Fred Wiliamson",
        "-",
    ],
]


def test_tabular_parse():
    assert tabular.parse() == cells


def test_tabular_to_dataframe():
    pd.testing.assert_frame_equal(tabular.to_dataframe(), pd.DataFrame(cells))
