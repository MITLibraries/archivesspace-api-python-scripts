import json
import logging
import os

from asnake.client import ASnakeClient
import pytest
import requests_mock

from asaps import models


@pytest.fixture
def as_ops():
    client = ASnakeClient(baseurl='mock://example.com', username='test',
                          password='test')
    as_ops = models.AsOperations(client)
    return as_ops


def test_get_record(as_ops):
    """Test get_record method."""
    with requests_mock.Mocker() as m:
        uri = '/repositories/2/resources/423'
        json_object = {'jsonmodel_type': 'resource'}
        m.get(uri, json=json_object)
        response = as_ops.get_record(uri)
        assert response == json_object


def test_create_endpoint(as_ops):
    """Test create_endpoint method."""
    rec_type = 'resource'
    repo_id = '0'
    endpoint = as_ops.create_endpoint(rec_type, repo_id)
    assert endpoint == 'repositories/0/resources'


def test_get_all_records(as_ops):
    """Test get_all_records method."""
    with requests_mock.Mocker() as m:
        endpoint = '/repositories/0/resources'
        json_object = [1, 2, 3, 4]
        m.get('/repositories/0/resources?all_ids=true', json=json_object)
        ids = as_ops.get_all_records(endpoint)
        assert ids == [1, 2, 3, 4]


def test_record_is_modified():
    record = models.Record()
    assert not record.modified
    record['title'] = "I am different"
    assert record.modified


def test_record_flush_persists_changes():
    record = models.Record()
    record['title'] = 'I am a title'
    assert record.modified
    record.flush()
    assert not record.modified


def test_changes_returns_json_patch_operations():
    record = models.Record()
    record['title'] = 'I am a title'
    assert record.changes == \
        [{'op': 'add', 'path': '/title', 'value': 'I am a title'}]


def test_search(as_ops):
    """Test search method."""
    with requests_mock.Mocker() as m:
        string = 'string'
        repo_id = '0'
        rec_type = 'resource'
        field = 'acqinfo'
        json_object = [{'uri': '1234'}]
        url = f'/repositories/{repo_id}/search?'
        m.get(url, json=json_object)
        results = as_ops.search(string, repo_id, rec_type, field)
        for result in results:
            assert result == json_object[0]['uri']


def test_save_record(as_ops, caplog):
    """Test post_record method."""
    caplog.set_level(logging.INFO)
    with requests_mock.Mocker() as m:
        rec_obj = models.Record()
        uri = '/repositories/2/resources/423'
        dry_run = 'False'
        rec_obj['uri'] = uri
        json_object = {'post': 'Success'}
        m.post(uri, json=json_object)
        as_ops.save_record(rec_obj, dry_run)
        message = json.loads(caplog.messages[0])['event']
        assert message == json_object


def test_post_new_record(as_ops):
    """Test post_new_record method."""
    with requests_mock.Mocker() as m:
        endpoint = '/repositories/0/resources'
        json_object = {'status': 'Created'}
        rec_obj = {'title': 'Test title'}
        m.post(endpoint, json=json_object)
        resp = as_ops.post_new_record(rec_obj, endpoint)
        assert resp['status'] == 'Created'


def test_create_arch_obj(as_ops):
    """Test create_arch_obj method."""
    title = 'Test title'
    level = 'series'
    notes = []
    agents = [{'ref': '/agents/123'}]
    parent = '/repositories/0/archival_objects/123'
    resource = '/repositories/0/resources/456'
    arch_obj = as_ops.create_arch_obj(title, level, agents, notes,
                                      parent, resource)
    assert arch_obj['title'] == title
    assert arch_obj['level'] == level
    assert arch_obj['linked_agents'] == agents
    assert arch_obj['parent']['ref'] == parent
    assert arch_obj['resource']['ref'] == resource


def test_create_dig_obj(as_ops):
    """Test create_dig_obj method."""
    title = 'Test title'
    link = '/repositories/0/digital_objects/123'
    dig_obj = as_ops.create_dig_obj(title, link)
    assert dig_obj['title'] == title
    assert dig_obj['digital_object_id'] == link


def test_create_note(as_ops):
    """Test create_note method."""
    content = 'Test content'
    label = 'Scope and Content Note'
    type = 'scopecontent'
    note = as_ops.create_note(type, label, content)
    assert note['label'] == label
    assert note['subnotes'][0]['content'] == content
    assert note['type'] == type


def test_create_agent_link(as_ops):
    """Test create_agent_link method."""
    agent_uri = '/agents/123'
    role = 'pbl'
    relator = 'creator'
    agent_link = as_ops.create_agent_link(agent_uri, role, relator)
    assert agent_link['ref'] == agent_uri
    assert agent_link['role'] == role
    assert agent_link['relator'] == relator


def test_link_dig_obj(as_ops):
    """Test link_dig_obj method."""
    arch_obj = {'instances': []}
    dig_obj_uri = '/repositories/0/digital_objects/123'
    arch_obj = as_ops.link_dig_obj(arch_obj, dig_obj_uri)
    assert arch_obj['instances'][0]['digital_object']['ref'] == dig_obj_uri


def test_save_record_flushes_changes(as_ops):
    with requests_mock.Mocker() as m:
        uri = '/foo/bar/1'
        dry_run = 'False'
        m.post(uri, json={'post': 'Success'})
        r = models.Record({'uri': uri})
        r['title'] = 'A title'
        assert r.modified
        as_ops.save_record(r, dry_run)
        assert not r.modified


def test_get_aos_for_resource(as_ops):
    """Test get_aos_for_resource method."""
    with requests_mock.Mocker() as m:
        resource = '/repositories/2/resources/423'
        json_object = {'record_uri': '/archival_objects/1234', 'children':
                       [{'record_uri': '/archival_objects/5678'}]}
        m.get(f'{resource}/tree', json=json_object)
        aolist = as_ops.get_aos_for_resource(resource)
        assert '/archival_objects/5678' in aolist


def test_update_dig_obj_link(as_ops):
    """Test update_dig_obj_link method."""
    update = 'TEST'
    do = {'digital_object_id': 'fish', 'file_versions': [{'file_uri':
          'fish'}]}
    do = as_ops.update_dig_obj_link(do, update)
    assert do['digital_object_id'] == update
    for file_version in do['file_versions']:
        assert file_version['file_uri'] == update


def test_audit():
    """"Test audit function."""
    sample_record = {'uri': '123'}
    change = {'op': 'add', 'path': '/title', 'value': 'I am a title'}
    msg = models.audit(record=sample_record, **change)
    assert msg == {'uri': '123', 'field': '/title', 'old': None,
                   'new': 'I am a title'}


def test_concat_id():
    """"Test concat_id function."""
    rec_obj = {'id_0': '1', 'id_1': '2', 'id_2': '3', 'id_3': '4'}
    coll_id = models.concat_id(rec_obj)
    assert coll_id == '1-2-3-4'


# How to test this?
# def test_create_csv_from_log():
#   """"Test create_csv_from_log function."""
#     assert False


def test_download_json():
    """Test download_json function."""
    rec_obj = models.Record()
    rec_obj['uri'] = '/test/123'
    path = models.download_json(rec_obj)
    assert os.path.isfile(path)
    os.remove(path)


def test_extract_note_field():
    """"Test extract_note_field function."""
    field = 'acqinfo'
    rec_obj = {'notes': [{'type': 'acqinfo', 'subnotes': [{'content':
               'test value'}]}]}
    report_dict = {'uri': '123', 'title': 'Title', 'id': '456'}
    report_dicts = models.extract_note_field(field, rec_obj, report_dict)
    for report_dict in report_dicts:
        assert report_dict['uri'] == '123'
        assert report_dict['acqinfo'] == 'test value'


def test_extract_obj_field():
    """"Test extract_obj_field function."""
    field = 'dates'
    rec_obj = {'dates': [{'begin': '1900', 'end': '1901', 'date_type':
               'inclusive'}]}
    report_dict = {'uri': '123', 'title': 'Title', 'id': '456'}
    obj_field_dict = {'dates': ['begin', 'end', 'expression', 'label',
                      'date_type']}
    report_dicts = models.extract_obj_field(field, rec_obj, obj_field_dict,
                                            report_dict)
    for report_dict in report_dicts:
        assert report_dict['uri'] == '123'
        assert report_dict['begin'] == '1900'
        assert report_dict['end'] == '1901'
        assert report_dict['date_type'] == 'inclusive'


def test_filter_note_type():
    """Test filter_note_type function."""
    rec_obj = {'notes': [{'note_type': 'acqinfo'}, {'note_type': 'bioghist'}]}
    notes = models.filter_note_type(rec_obj, 'acqinfo')
    for note in notes:
        assert note['note_type'] == 'acqinfo'


def test_find_key():
    """Test find_key function."""
    nest_dict = {'children': [{'publish': True, 'children': [{'publish':
                 True}]}]}
    keys = models.find_key(nest_dict, 'children')
    key_count = 0
    for key in keys:
        key_count += 1
    assert key_count == 2
