import requests_mock


def test_get_record(self):
    """Test get_record function."""
    with requests_mock.Mocker() as m:
        m.get('/repositories/2/resources/423', text='Passed')
        uri = '/repositories/2/resources/423'
        response = self.client.auth_client.get(uri).text
        assert response == 'Passed'


def test_download_json(self):
    """Test download_json function."""
    pass
