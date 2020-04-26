# Getting reports

## The simple case

This is the simplest way to get a report:

```python
rf.get_report("00O1a000001YtFG")
```

In this way, no **filters** are applied and you will get 2000 rows at max.

## Getting more than 2000 rows

If you just want all the data, the only work around is to provide the name of a
column to be used as a unique identifier for each row.

Unfortunately, this is needed because the API doesn't provide a way to limit by
a number of rows or something more convenient like that.

```python
rf.get_report("00O1a000001YtFG", id_column="ID_COLUMN")
```

## Filtering by dates

You can also filter the report by dates on the fly:

```python
rf.get_report("00O1a000001YtFG", start="01 December, 2019", end="31/01/2020")
```

!!! note
    To avoid ambiguity, days must come first.

By default, this will use the standard date filter column that is in the
report. You may change it with the `date_column` argument.

```python
rf.get_report("00O1a000001YtFG", start="01/12/2020", date_column="Last Modification Date")
```

## Filtering a column

If you want to filter the report by a report column, you may do it by passing a
list of tuples to the filters parameter:

```python
rf.get_report("00O1a000001YtFG", filters=[("Sales Revenue", ">=", 3000)])
```

You can use the typical logical operators as in Python, e.g.
`!=`, `==` etc., but also `contains`, `not contains` and `startswith`.

## Adding filter logic

When filtering, you may find it useful to add a logic to your filters:

```python
rf.get_report("00O1a000001YtFG", filters=[("Account", "==", "Mary")], logic="1 AND 2")
```

## Customizing request calls

Every keyword arguments is passed to the POST request call (done by the `requests` library).

You can take advantage of that to customize the URL query, for example:

```python
rf.get_report("00O1a000001YtFG", params={"includeDetails": "false"})
```

## Downloading report as Excel spreadsheet

You can download the entire report (the 2000 row limit does not apply here) as
an Excel spreadsheet:

```python
rf.get_report("00O1a000001YtFG", excel=True)
```

The spreadsheet will then be saved to your current working directory with an
appropriate name.

But you may also pass a string to give the file the name you want.

```python
rf.get_report("00O1a000001YtFG", excel="spreadsheet.xlsx")
```

!!! note
    This still struggles if the report is huge. It's common to hang for a while
    until it starts to be saved by chunks.

## Speeding up

Unfortunately, this package struggles with performance, although I'm really
trying my best to make it work.

You can speed up things a little by monkeypatching the json parser library:

```python
import requests
import ujson

requests.models.complexjson = ujson
```
