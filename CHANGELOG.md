# 0.0.5

- Add helpful prompt to get user credentials via standarad input (input and
  getpass functions) , e.g.: "Password: ".

# 0.0.4

- Allow user to authenticate with Salesforce object without any arguments,
  which will means he is going to provide the credentials via standard input.
- Escape user credentials in XML body for logging in via SOAP API, closes #2.
- Allow user to pass domain when using Reportforce, closes #4.

# 0.0.3

- Fix bug of reportforce.helpers not being a package (withou a __init__.py file).
