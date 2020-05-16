# 0.0.7

- Huge refactoring towards a more OOP approach regarding the report parsers
  etc.
- Remove `Reportforce.get_total`.
- Add optional parameter to ignore standard date filter into
  `Reportforce.get_report`, named `ignore_date_filter`. Useful if by default
  there is only dates in current month but you want to get dates in another
  month, without needing to create a report.
- Add support to filter by `date_duration`, e.g., "This month", "Last month",
  "Current Fiscal Year", etc.

# 0.0.6

- Fix bug of domain defaulting to `None` in Salesforce object.

# 0.0.5

- Add helpful prompt to get user credentials via standarad input (input and
  getpass functions) , e.g.: "Password: ".

# 0.0.4

- Allow user to authenticate with Salesforce object without any arguments,
  which will means he is going to provide the credentials via standard input.
- Escape user credentials in XML body for logging in via SOAP API, closes #2.
- Allow user to pass domain when using Reportforce, closes #4.

# 0.0.3

- Fix bug of reportforce.helpers not being a package (withou a `__init__.py` file).
