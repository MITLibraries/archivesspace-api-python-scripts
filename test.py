import asOps


def test_createclient():
    """Test createclient function."""
    secfilelist = ['secretsProd', '', 'secrets', '#$%#%##@']
    for secfile in secfilelist:
        client = asOps.createclient(secfile)
        assert client.get('repositories').status_code == 200
    return client


# in progress
def test_getrecord():
    """Test getrecord function."""
    pass
    # asOpsRev.getrecord()


def test_constructor():
    """Test constructor function."""
    pass
    # asOpsRev.constructor()


def test_downloadjson():
    """Test downloadjson function."""
    pass
    # asOpsRev.downloadjson()
