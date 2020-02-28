import urllib
import xml.etree.ElementTree as ET

namespace = {
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "urn": "urn:partner.soap.sforce.com",
}


def read_successful_response(response):
    """Parse XML returned by SOAP API response in case of a successful login.

    Parameters
    ----------
    response : str
        SOAP API response in text.

    Returns
    -------
    tuple
        Session id and instance url.
    """
    xml_tree = ET.fromstring(response)

    session_id_path = "soapenv:Body/urn:loginResponse/urn:result/urn:sessionId"
    session_id = xml_tree.findtext(session_id_path, namespaces=namespace)

    server_url_path = "soapenv:Body/urn:loginResponse/urn:result/urn:serverUrl"
    server_url = xml_tree.findtext(server_url_path, namespaces=namespace)

    instance = urllib.parse.urlparse(server_url).hostname
    return session_id, instance


def read_failed_response(response):
    """Parse XML returned by SOAP API response in case of a failed login.

    Parameters
    ----------
    response : str
        SOAP API response in text.

    Returns
    -------
    str
        A string describing the error.
    """
    xml_tree = ET.fromstring(response)
    return xml_tree.findtext(
        "soapenv:Body/soapenv:Fault/faultstring", namespaces=namespace
    )
