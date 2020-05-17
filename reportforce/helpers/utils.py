import pandas as pd


def is_iterable(v):
    if isinstance(v, str):
        return False
    try:
        iter(v)
        return True
    except TypeError:
        return False


def surround_with_quotes(s):
    return f'"{s}"'


def reset_useless_index(df):
    if isinstance(df.index, pd.MultiIndex):
        return df
    else:
        return df.reset_index(drop=True)
