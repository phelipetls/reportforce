import pandas as pd

from reportforce.helpers import utils


class TestIsIterable:
    def test_is_iterable_list(self):
        assert utils.is_iterable([1, 2, 3])


    def test_is_iterable_tuple(self):
        assert utils.is_iterable((1, 2, 3))


    def test_is_iterable_generator(self):
        assert utils.is_iterable((x for x in range(3)))


    def test_is_iterable_string(self):
        assert not utils.is_iterable("string")


    def test_is_iterable_pandas_series(self):
        assert utils.is_iterable(pd.Series([1, 2, 3]))

class TestSurroundWithQuotes:
    def test_surround_with_quotes_string(self):
        assert utils.surround_with_quotes("1") == '"1"'

    def test_surround_with_quotes_string(self):
        assert utils.surround_with_quotes(1) == '"1"'
