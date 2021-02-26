import csv
import json
import logging

from asnake.client import ASnakeClient
from click.testing import CliRunner
import pytest
import requests_mock

from asaps import models, workflows


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def as_ops():
    client = ASnakeClient(baseurl='mock://example.com', username='test',
                          password='test')
    as_ops = models.AsOperations(client)
    return as_ops


def test_export_metadata(as_ops):
    """Test export_metadata method."""
    with requests_mock.Mocker() as m:
        resource = '/repositories/0/resources/423'
        repo_id = '0'
        field = 'ref_id'
        ao_uri = '/repositories/0/archival_objects/1234'
        json_object_1 = {'record_uri': ao_uri}
        json_object_2 = {'uri': ao_uri, 'ref_id':
                         'a2b2c2', 'display_string': 'Sample Title'}
        m.get(f'{resource}/tree', json=json_object_1)
        m.get(ao_uri, json=json_object_2)
        report_dicts = workflows.export_metadata(as_ops, resource, field,
                                                 repo_id)
        for report_dict in report_dicts:
            assert report_dict['uri'] == ao_uri
            assert report_dict['title'] == 'Sample Title'
            assert report_dict['file_identifier'] == 'a2b2c2'


def test_create_new_dig_objs(as_ops, caplog, runner):
    """Test create_new_dig_objs method."""
    caplog.set_level(logging.INFO)
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('metadata.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['uri'] + ['link'])
                writer.writerow(['/repositories/0/archival_objects/1234'] +
                                ['mock://example.com/handle/111.1111'])
            ao_uri = 'mock://example.com/repositories/0/archival_objects/1234'
            dos_uri = 'mock://example.com/repositories/0/digital_objects'
            do_uri = '/repositories/0/digital_objects/5678'
            json_object_1 = {'uri': '/repositories/0/archival_objects/1234',
                             'display_string': 'Sample Title',
                             'instances': []}
            json_object_2 = {'post': 'Success', 'uri': do_uri}
            json_object_3 = {'post': 'Success'}
            m.get(ao_uri, json=json_object_1)
            m.post(dos_uri, json=json_object_2)
            m.post(ao_uri, json=json_object_3)
            workflows.create_new_dig_objs(as_ops, 'metadata.csv', '0')
            message_1 = json.loads(caplog.messages[1])['event']
            message_2 = json.loads(caplog.messages[2])['event']
            assert message_1 == json_object_2
            assert message_2 == json_object_3
