import re
import numpy as np
import pandas as pd

from .helpers import parsers
from .helpers import generators

URL = "https://{}/services/data/v{}/analytics/reports/{}"


def get_excel(report_id, excel, metadata, salesforce, **kwargs):
    """Download report as formatted Excel spreadsheet.

    Parameters
    ----------
    report_id : str
        A report unique identifier.

    excel : bool or str
        If a non-empty string, it will be used as the
        filename. If True, the workbook is automatically
        named.

    salesforce : object
        An instance of simple_salesforce.Salesforce or
        reportforce.login.Login, needed for authentication.
    """

    url = URL.format(salesforce.instance_url, salesforce.version, report_id)

    headers = salesforce.session.headers.copy()

    headers.update(
        {"Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    )

    with salesforce.session.post(
        url, headers=headers, json=metadata, stream=True, **kwargs
    ) as response:
        if isinstance(excel, str):
            filename = excel
        elif excel:
            string = response.headers["Content-Disposition"]
            pattern = 'filename="(.*)"'
            filename = re.search(pattern, string).group(1)

        with open(filename, "wb") as excel_file:
            for chunk in response.iter_content(chunk_size=512 * 1024):
                if chunk:
                    excel_file.write(chunk)
