from reportforce import Reportforce


def test_get_metadata(mock_login, mocker):

    mock_get_metadata = mocker.patch.object(Reportforce.session, "get")

    EXPECTED_URL = (
        "https://www.salesforce.com/"
        "services/data/v47.0/analytics"
        "/reports/ID/describe"
    )

    rf = Reportforce("foo@bar.com", "1234", "XXX")
    rf.get_metadata("ID")

    mock_get_metadata.assert_called_with(EXPECTED_URL)
