reportforce: a python module to get Salesforce reports
======================================================

If you ever needed a way to download Salesforce reports to do some kind
of analysis, say, in Excel, and cursed it because it gets so tedious to
do it manually in the browser, this package may be of help.

It aims to ease the task of getting a Salesforce report, by downloading
and parsing it into a pandas DataFrame.

AND the **killer feature**: a workaround the 2000 row limit! Let's see
how this works.

First, we will need to authenticate. This is how you can do it:

Authenticating
--------------

.. code:: python

    from reportforce.login import Login

    session = Login(username="foo@bar.com", password="1234", security_token="XXX")

You may also choose to use the more sophisticated
simple_salesforce module to get a session object to authenticate
your requests.

Getting report, the simple way
------------------------------

Now, if your report is less than 2000 lines. No need to worry much, this
is all you need to do:

.. code:: python

    from reportforce.report import get_report

    get_report("REPORTID", session=session)

Getting more than 2000 rows
---------------------------

But!! If it has more than 2000 rows and you want all of them, you'll
need to provide a column name that has a unique value for each row. Yes,
this is needed because the API doesn't provide a way to limit by row
number etc.

.. code:: python

    get_report("REPORTID", id_column="COLUMN_WITH_UNIQUE_VALUES", session=session)

Filtering by dates
------------------

You can also filter the report by dates on the fly:

.. code:: python

    get_report("REPORTID", start="01 December, 2019", end="31/01/2020", session=session)

Filtering arbitrary columns
---------------------------

And, if you want to filter a report field, you may do it like this:

.. code:: python

    get_report("REPORTID", filters=[("FILTER_COLUMN", ">=", "VALUE")]

Adding filter logic
-------------------

It may be needed to add a logic to your filters, usually when there is
already one in the report. You can do it as follows:

.. code:: python

    get_report("REPORTID", logic="1 AND 2")
