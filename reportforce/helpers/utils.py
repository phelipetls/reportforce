def is_iterable(v):
    if isinstance(v, str):
        return False
    try:
        iter(v)
        return True
    except:
        return False

def surround_with_quotes(s):
    return f'"{s}"'