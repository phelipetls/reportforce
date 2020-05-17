# 0.0.7

- Huge refactoring towards a more OOP approach regarding the report parsers,
  filtering etc.
- Remove `Reportforce.get_total`.
- Add optional parameter to ignore standard date filter into
  `Reportforce.get_report`, named `ignore_date_filter`. Useful if the standard
  date filter conflicts with another date filter passed into `filters`.
- Add support to filter by `date_interval`, e.g., "This month", "Last month",
  "Current Fiscal Year", etc.

# 0.0.6

- Fix bug of domain defaulting to `None` in Salesforce object.

# 0.0.5

- Add helpful prompt to get user credentials via standarad input (input and
  getpass functions) , e.g.: "Password: ".

# 0.0.4

- Allow user to authenticate with Salesforce object via standard input.
- Escape user credentials in XML body for logging in via SOAP API.
- Allow user to pass domain when using Reportforce.

# 0.0.3

- Fix bug of reportforce.helpers not being a package (without a `__init__.py` file).
