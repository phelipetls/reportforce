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
rf.get_report("00O1a000001YtFG", id_column="Case Number")
```

## Filtering by dates

You can also customize the standard date filter like so:

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

It's also possible to filter by an arbitrary date interval.

```python
rf.get_report("00O1a000001YtFG", date_interval="Current Fiscal Year")
```

## Filtering a column

If you want to filter the report by a report column, you may do it by passing a
list of tuples to the filters parameter:

```python
rf.get_report("00O1a000001YtFG", filters=[("Sales Revenue", ">=", 3000)])
```

You can use the typical logical operators as in Python, e.g.
`!=`, `==` etc., but also `contains`, `not contains` and `startswith`.

To pass more than one value to the filter, just pass an iterable like a list or a tuple:

```python
rf.get_report(
    "00O1a000001YtFG", filters=[("Closed Date", "==", ["01-02-2020", "02-02-2020"])]
)
```

You can filter by columns that are not included in the report's details also,
i.e., columns that are not displayed in the rows.

## Adding filter logic

When filtering, you may find it useful to add a logic to your filters:

```python
rf.get_report("00O1a000001YtFG", filters=[("Account", "==", "Mary")], logic="1 AND 2")
```

If there already is a logic and you add a filter, you will have to update the
underlying logic accordingly, otherwise the API will thrown an error.

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
