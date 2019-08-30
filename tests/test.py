from asaps.models import Client


def test_createclient():
    """Test createclient function."""
    secfilelist = ['secretsProd', 'secretsDev']
    for secfile in secfilelist:
        print(secfile)
        client = Client(secfile)
        assert client.auth_client.get('repositories').status_code == 200


def test_getrecord():
    """Test getrecord function."""
    pass


def test_downloadjson():
    """Test downloadjson function."""
    pass


def test_basepop():
    """Test basepop function."""
    pass


def test_classpop():
    """Test classpop function."""
    pass
