# Authentication

## Security Token

First of all, you'll need to authenticate your calls somehow.

Here is one way to do it, using your username, password and security token:

```python
from reportforce import Reportforce

rf = Reportforce(username="foo@bar.com", password="1234", security_token="token")
```

!!! note
    Information on how to get your security token
    [here](https://help.salesforce.com/articleView?id=user_security_token.htm&type=5).
    You can usually find it in your e-mail box though.

## Other methods

Alternatively, you could pass the Session ID and the Salesforce instance URL
directly.

This may be useful if you want a more sophisticated method of authentication,
hopefully supported by a library as
[`simple_salesforce`](https://github.com/simple-salesforce/simple-salesforce).

```python
from simple_salesforce import Salesforce

sf = Salesforce(username="foo@bar.com", password="1234", security_token="token")

rf = Reportforce(session_id=sf.session_id, instance_url=sf.sf_instance)
```

Now you're all set, head over to the [Usage](./usage.md) section to start
getting data.

## Troubleshooting

By default, it is assumed that your Salesforce server supports the version 47.0
of the Analytics and SOAP API.

If that is not the case, please pass the right version to the `version`
parameter when logging in.

```python
rf = Reportforce(
    username="foo@bar.com", password="1234", security_token="token", version="32.0"
)
```

If you don't have a clue how to find that, try this
[link](https://help.salesforce.com/articleView?id=000334996&type=1&mode=1).

You can also assure yourself to have the Analytics API latest version by
passing `latest_version=True` when authenticating.
