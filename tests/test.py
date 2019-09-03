import requests_mock


# how call client for test
def test_get_record(client):
    """Test get_record function."""
    with requests_mock.Mocker() as m:
        m.get('/repositories/2/resources/423', text='Passed')
        uri = '/repositories/2/resources/423'
        response = client.auth_client.get(uri).text
        assert response == 'Passed'


def test_download_json():
    """Test download_json function."""
    pass
