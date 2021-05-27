import logging
import os

from asnake.client import ASnakeClient
from click.testing import CliRunner
import pytest
import requests_mock
import structlog

from asaps import models


@pytest.fixture(autouse=True)
def as_mock():
    with requests_mock.Mocker() as m:
        ids_json = [423, 756]
        m.get('/repositories/0/resources?all_ids=true',
              json=ids_json)
        res_json_1 = {'jsonmodel_type': 'resource', 'id_0': 'AB',
                      'id_1': '123', 'title': 'Test title 1',
                      'uri': '/repositories/0/resources/423',
                      'ref_id': 'a1b_2c3',
                      'notes': [{'type': 'acqinfo', 'subnotes': [{'content':
                                'test value'}]}]}
        m.get('/repositories/0/resources/423', json=res_json_1)
        res_json_2 = {'jsonmodel_type': 'resource',
                      'uri': '/repositories/0/resources/756',
                      'title': 'Test title 2', 'notes': []}
        m.get('/repositories/0/resources/756', json=res_json_2)
        upd_json = {'post': 'Success'}
        m.post('/repositories/0/resources/423', json=upd_json)
        tree_json = {'record_uri': '/repositories/0/archival_objects/1234',
                     'children':
                     [{'record_uri': '/repositories/0/archival_objects/5678'}]}
        m.get('/repositories/2/resources/423/tree', json=tree_json)
        crtd_json = {'status': 'Created'}
        m.post('/repositories/0/resources', json=crtd_json)
        search_json = [{'uri': '/repositories/0/archival_objects/1234'}]
        m.get('/repositories/0/search?', json=search_json)
        tree_json = {'record_uri': '/repositories/0/archival_objects/1234'}
        m.get('/repositories/0/resources/423/tree', json=tree_json)
        ao_json = {'uri': '/repositories/0/archival_objects/1234',
                   'ref_id': 'a2b2c2', 'display_string': 'Sample Title',
                   'instances': [{'instance_type': 'mixed_materials'}],
                   'notes': [{'type': 'acqinfo', 'subnotes':
                             [{'content': 'test value'}]}]}
        m.get('/repositories/0/archival_objects/1234', json=ao_json)
        ao_upd_json = {'post': 'Success'}
        m.post('/repositories/0/archival_objects/1234', json=ao_upd_json)
        do_crtd_json = {'post': 'Success',
                        'uri': '/repositories/0/digital_objects/5678'}
        m.post('/repositories/0/digital_objects', json=do_crtd_json)
        ag_crtd_json = {'status': 'Created', 'uri': '/agents/people/789'}
        m.post('/agents/people', json=ag_crtd_json)
        ao_crtd_json = {'status': 'Created', 'uri':
                        '/repositories/0/archival_objects/1234'}
        m.post('/repositories/0/archival_objects', json=ao_crtd_json)
        do_json = {'file_versions': [{}],
                   'uri': '/repositories/0/digital_objects/5678'}
        m.get('/repositories/0/digital_objects/5678', json=do_json)
        do_upd_json = {'post': 'Success'}
        m.post('/repositories/0/digital_objects/5678', json=do_upd_json)
        top_con_json = {'post': 'Success',
                        'uri': '/repositories/0/top_containers/1234'}
        m.post('/repositories/0/top_containers', json=top_con_json)
        yield m


@pytest.fixture
def as_ops():
    client = ASnakeClient(baseurl='mock://example.com', username='test',
                          password='test')
    as_ops = models.AsOperations(client)
    return as_ops


@pytest.fixture(autouse=True, scope='session')
def logger():
    logger = structlog.get_logger()
    logging.basicConfig(format="%(message)s",
                        handlers=[logging.StreamHandler()], level=logging.INFO)
    return logger


@pytest.fixture()
def output_dir(tmp_path):
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    return str(f'{output_dir}/')


@pytest.fixture()
def package_directory(tmp_path):
    main_dir = tmp_path / '2021_001BB_001'
    main_dir.mkdir()
    objects_dir = os.path.join(main_dir, 'data/2021_001BB_001/objects/access')
    os.makedirs(objects_dir)
    with open(f'{objects_dir}/00-000001234.pdf', 'w'):
        pass
    return str(f'{main_dir}/')


@pytest.fixture(autouse=True)
def runner():
    return CliRunner()
