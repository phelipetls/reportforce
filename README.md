# reportforce: A Python package to turn Salesforce reports into DataFrames

-   [Main Features](#main-features)
-   [Example Usage](#example-usage)
    -   [Authenticating](#authenticating)
    -   [Getting a report, the simple way](#getting-a-report-the-simple-way)
    -   [Getting more than 2000 rows](#getting-more-than-2000-rows)
    -   [Filtering by dates](#filtering-by-dates)
    -   [Filtering an arbitrary column](#filtering-an-arbitrary-column)
    -   [Adding filter logic](#adding-filter-logic)
-   [License](#license)
-   [Contributing](#contributing)
-   [Support](#support)


Ever needed to routinely download a Salesforce report and curse your
life because it gets so tedious to so manually in the browser? Well, me too.
That's why I created this package.

It aims to ease the task of getting a Salesforce report. It does so by
requesting the report JSON via Analytics API and then parsing it into a
DataFrame.

## Main Features

-   Supports multiple report formats, such as tabular, matrix and summary.
-   A **workaround the 2000 row limit** if you provide a column with unique values.

## Example Usage

### Authenticating

First of all, you will need to authenticate your calls to a Salesforce server.

This is how you can do it:

``` python
from reportforce.login import Login

session = Login(username="foo@bar.com", password="1234", security_token="XXX")
```

You may also choose to use the more sophisticated
[simple\_salesforce](https://github.com/simple-salesforce/simple-salesforce)
module to get a session object to authenticate your requests.

### Getting a report, the simple way

Now, if your report is less than 2000 lines. No need to worry much, this
is all you need to do:

``` python
from reportforce import report

report.get_report("00O1a000001YtFG", session=session)
```

This will handle all report types.

### Getting more than 2000 rows

But!! If it has more than 2000 rows and you want all of them, you'll
need to provide a column name that has a unique value for each row.

Unfortunately, this is needed because the API doesn't provide a way to
limit by a number of rows or something like that.

``` python
report.get_report("00O1a000001YtFG", id_column="COLUMN_WITH_UNIQUE_VALUES", session=session)
```

### Filtering by dates

You can also filter the report by dates on the fly:

``` python
report.get_report("00O1a000001YtFG", start="01 December, 2019", end="31/01/2020", session=session)
```

Note though that, to avoid ambiguity, the day must come first.

By default, this will use the standard date filter column that is in the
report. You may change it with the `date_column` argument.

### Filtering an arbitrary column

If you want to filter a report field, you may do it by passing
a list of tuples to the filters parameter:

``` python
report.get_report("00O1a000001YtFG", filters=[("COLUMN_NAME", ">=", "VALUE")]
```

You can use your the typical logical operators as you would in Python, e.g.
"!=", "==" etc., but also "contains", "not contains" and "startswith".

### Adding filter logic

It may be needed to add a logic to your filters, usually when there is
already one in the report. Otherwise, you will get an error. You can do
it as follows:

``` python
report.get_report("00O1a000001YtFG", logic="1 AND 2")
```

## License

[MIT](https://github.com/phelipetls/seriesbr/blob/master/LICENSE)

## Contributing

If you find a bug, an issue would be much welcomed!
Likewise, if you think something could be improved,
feel free to open a pull request.

## Support

Give this a repo a start if you find if helpful. :)
