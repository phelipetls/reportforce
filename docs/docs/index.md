# A Salesforce Analytics API client in Python

Ever needed to daily download a Salesforce report and curse your life because
it gets so tedious to do so manually in the browser?

Well, me too. To help turning this process less painful, I created this
package. By using it, you will hopefully be able to download most Salesforce
reports as a *DataFrame* or an Excel *spreadsheet*.

Check out our [User Guide](user-guide) to start using the library.

# Main Features

-   Supports downloading tabular, matrix and summary reports.
-   Workaround the 2000 row limit if you provide a column with unique values.
-   Download reports as Excel files.
