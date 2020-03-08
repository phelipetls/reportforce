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
    ) as r:
        if isinstance(excel, str):
            filename = excel
        else:
            string = r.headers["Content-Disposition"]
            pattern = 'filename="(.*)"'
            filename = re.search(pattern, string).group(1)

        with open(filename, "wb") as excel_file:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    excel_file.write(chunk)


@generators.report_generator
def get_tabular_reports(url, metadata=None, salesforce=None, **kwargs):
    """Request and parse a tabular report.

    Parameters
    ----------
    url : str
        Report url.

    metadata : dict
        Used for filtering.

    session : object
        Used for authentication.

    Returns
    -------
    tuple
        JSON response body parsed as a dict,
        Report data cells parsed as a list,
        Indices to be used in the DataFrame.
    """
    tabular = salesforce.session.post(url, json=metadata, **kwargs).json()

    tabular_cells = parsers.get_tabular_cells(tabular)
    indices = None  # no meaningful indices here

    return tabular, tabular_cells, indices


@generators.report_generator
def get_matrix_reports(url, metadata, salesforce, **kwargs):
    """Request and parse a matrix report.

    Parameters
    ----------
    url : str
        Report url.

    metadata : dict
        Used for filtering.

    salesforce : object
        Used for authentication.

    Returns
    -------
    tuple
        JSON response body parsed as a dict,
        Report data cells parsed as a list,
        Indices to be used in the DataFrame.
    """
    matrix = salesforce.session.post(url, json=metadata, **kwargs).json()

    if len(matrix["factMap"]) == 1:
        return matrix, [], None

    matrix_cells = np.array(parsers.get_matrix_cells(matrix))

    groupings_down = matrix["groupingsDown"]["groupings"]
    names = parsers.get_groupings_labels(matrix, "groupingsDown")
    indices = pd.MultiIndex.from_tuples(parsers.get_groups(groupings_down), names=names)

    columns = parsers.get_columns(matrix)

    matrix_cells.shape = (len(indices), len(columns))
    return matrix, matrix_cells, indices


@generators.report_generator
def get_summary_reports(url, metadata, salesforce, **kwargs):
    """Request and parse a summary report.

    Parameters
    ----------
    url : str
        Report url.

    metadata : dict
        Used for filtering.

    salesforce : object
        Used for authentication.

    Returns
    -------
    tuple
        JSON response body parsed as a dict.
        Report fact map parsed as a list.
        Indices to be used in the DataFrame.
    """
    summary = salesforce.session.post(url, json=metadata, **kwargs).json()

    if len(summary["factMap"]) == 1:
        return summary, [], None

    summary_cells, cells_by_group = parsers.get_summary_cells(summary)
    indices = parsers.get_summary_indices(summary, cells_by_group)

    return summary, summary_cells, indices
