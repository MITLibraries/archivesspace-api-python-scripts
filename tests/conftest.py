import logging

from click.testing import CliRunner
import pytest
import requests_mock
import structlog


@pytest.fixture(autouse=True)
def as_mock():
    with requests_mock.Mocker() as m:
        ids_json = [1, 2, 3, 4]
        m.get('/repositories/0/resources?all_ids=true',
              json=ids_json)
        rec_json = {'jsonmodel_type': 'resource'}
        m.get('/repositories/2/resources/423', json=rec_json)
        upd_json = {'post': 'Success'}
        m.post('/repositories/0/resources/423', json=upd_json)
        tree_json = {'record_uri': '/archival_objects/1234', 'children':
                     [{'record_uri': '/archival_objects/5678'}]}
        m.get('/repositories/2/resources/423/tree', json=tree_json)
        crtd_json = {'status': 'Created'}
        m.post('/repositories/0/resources', json=crtd_json)
        search_json = [{'uri': '1234'}]
        m.get('/repositories/0/search?', json=search_json)
        yield m


@pytest.fixture(autouse=True, scope='session')
def logger():
    logger = structlog.get_logger()
    logging.basicConfig(format="%(message)s",
                        handlers=[logging.StreamHandler()], level=logging.INFO)
    return logger


@pytest.fixture(autouse=True)
def runner():
    return CliRunner()
