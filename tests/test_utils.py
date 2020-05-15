import pandas as pd

from reportforce.helpers.utils import is_iterable

def test_is_iterable_list():
    assert is_iterable([1, 2, 3])

def test_is_iterable_tuple():
    assert is_iterable((1, 2, 3))

def test_is_iterable_generator():
    assert is_iterable((x for x in range(3)))

def test_is_iterable_string():
    assert not is_iterable("string")

def test_is_iterable_pandas_series():
    assert is_iterable(pd.Series([1, 2, 3]))
