import getpass
import requests

from .helpers.xml import read_failed_response, read_successful_response


class Login(object):
    """
    A Salesforce session instance
    """

    def __init__(self, username, password, security_token, **kwargs):
        self.session_id, self.instance_url = soap_login(
            username, password, security_token, **kwargs
        )
        self.headers = {"Authorization": "Bearer " + self.session_id}


class AuthenticationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def soap_login(username, password, security_token, domain="login", version="47.0"):
    """
    Helper function to login into Salesforce via SOAP API.

    Parameters
    ----------
    username : str
        Username.

    password : str
        Password.

    security_token : str
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
    """
    soap_url = "https://{}.salesforce.com/services/Soap/u/{}".format(domain, version)
    soap_headers = {
        "Content-Type": "text/xml; charset=UTF-8",
        "SoapAction": "login",
    }
    soap_body = """<?xml version="1.0" encoding="utf-8" ?>
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
        username=username,
        password=password if password else getpass.getpass(),
        token=security_token if security_token else getpass.getpass("Security Token: "),
    )
    response = requests.post(soap_url, headers=soap_headers, data=soap_body)
    if response.status_code != 200:
        msg = read_failed_response(response.text)
        raise AuthenticationError(msg)
    return read_successful_response(response.text)
