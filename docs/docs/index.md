# A Salesforce Analytics API client for Python

[![Documentation Status](https://readthedocs.org/projects/reportforce/badge/?version=latest)](https://reportforce.readthedocs.io/en/latest/?badge=latest)
[![PyPI Version](https://img.shields.io/pypi/v/reportforce.svg)](https://pypi.org/project/reportforce/)
[![Travis Build Status](https://travis-ci.org/phelipetls/reportforce.svg?branch=master)](https://travis-ci.org/phelipetls/reportforce)
[![Code Coverage](https://codecov.io/gh/phelipetls/reportforce/branch/master/graph/badge.svg)](https://codecov.io/gh/phelipetls/reportforce)

Ever needed to daily download a Salesforce report and curse your life because
it gets so tedious to do it manually in the browser?

Well, me too. To help turning this process less painful, I created this
package. By using it, you will hopefully be able to download most Salesforce
reports as a *DataFrame* or an Excel *spreadsheet*.

Check out our [User Guide](user-guide) to start using the library.

# Main Features

-  Supports downloading tabular, matrix and summary reports.
-  Workaround the 2000 row limit if you provide a column that acts as an
   identifier for each row.
-  Download reports as Excel files.
