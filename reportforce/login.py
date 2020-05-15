import requests

from getpass import getpass
from xml.sax.saxutils import escape

from .helpers.xml import read_failed_response, read_successful_response

DEFAULT_VERSION = "47.0"
SOAP_HEADERS = {
    "Content-Type": "text/xml; charset=UTF-8",
    "SoapAction": "login",
}


class Salesforce:
    """A Salesforce session instance.

    Attributes
    ----------
    session_id : str
        Session ID passed to the request headers for authentication.

    instance_url : str
        The user's Salesforce instance/server.

    version : str, default '47.0'
        The SOAP API and Analytics API version to be used.

    headers : dict
        Headers used for authentication.

    Methods
    -------
    _get_latest_version : str
        Method used to get the latest Analytics API version.

    Raises
    ------
    AuthenticationError
        If anything goes wrong while authenticating.
    """

    def __init__(
        self,
        username=None,
        password=None,
        token=None,
        version=DEFAULT_VERSION,
        domain="login",
        session_id=None,
        instance_url=None,
        latest_version=False,
    ):
        if instance_url and session_id:
            self.session_id = session_id
            self.instance_url = instance_url

        else:
            self.session_id, self.instance_url = soap_login(
                username, password, token, version, domain
            )

        self.version = self._get_latest_version() if latest_version else version
        self.headers = {"Authorization": "Bearer {}".format(self.session_id)}

    def _get_latest_version(self):
        url = "https://{}/services/data/".format(self.instance_url)
        version = requests.get(url).json()[-1]["version"]
        return version


def soap_login(
    username=None, password=None, token=None, version="47.0", domain="login"
):
    """Login into Salesforce via SOAP API.

    Parameters
    ----------
    username : str
        Username.

    password : str
        Password.

    token : str
        The security token. This is normally provided when
        you change your password via e-mail.

    domain : str
        Domain. Either 'login' or 'test', login by default.

    version : str
        Latest available version in your Salesforce server.

    Returns
    -------
    tuple
        A tuple containing the session id and instance url.

    Raises
    ------
    AuthenticationError
        If anything goes wrong while authenticating.
    """

    soap_url = generate_soap_url(domain, version)
    soap_body = generate_soap_body(username, password, token)

    response = requests.post(soap_url, headers=SOAP_HEADERS, data=soap_body)

    if response.status_code != 200:
        msg = read_failed_response(response.text)
        raise AuthenticationError(msg)

    return read_successful_response(response.text)


def generate_soap_url(domain, version):
    return f"https://{domain}.salesforce.com/services/Soap/u/{version}"


def generate_soap_body(username=None, password=None, token=None):
    username = escape(username or input("Username: "))
    password = escape(password or getpass("Password: "))
    token = escape(token or getpass("Security token: "))

    return """<?xml version="1.0" encoding="utf-8" ?>
    <env:Envelope
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <env:Body>
            <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                <n1:username>{username}</n1:username>
                <n1:password>{password}{token}</n1:password>
            </n1:login>
        </env:Body>
    </env:Envelope>""".format(
        username=username, password=password, token=token
    )


class AuthenticationError(Exception):
    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return self.msg
