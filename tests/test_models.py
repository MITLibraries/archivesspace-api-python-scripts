import json
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
    """Test create_endpoint function."""
    rec_type = 'resource'
    repo_id = '0'
    endpoint = as_ops.create_endpoint(rec_type, repo_id)
    assert endpoint == 'repositories/0/resources'


def test_get_all_records(as_ops):
    """Test get_all_records function."""
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
        note_type = 'acqinfo'
        json_object = [{'uri': '1234'}]
        url = f'/repositories/{repo_id}/search?'
        m.get(url, json=json_object)
        results = as_ops.search(string, repo_id, rec_type, note_type)
        for result in results:
            assert result == json_object[0]['uri']


def test_save_record(as_ops, caplog):
    """Test post_record method."""
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
    """Test get_aos_for_resource function."""
    with requests_mock.Mocker() as m:
        resource = '/repositories/2/resources/423'
        json_object = {'record_uri': '/archival_objects/1234', 'children':
                       [{'record_uri': '/archival_objects/5678'}]}
        m.get(f'{resource}/tree', json=json_object)
        aolist = as_ops.get_aos_for_resource(resource)
        assert '/archival_objects/5678' in aolist


def test_extract_fields(as_ops, caplog):
    """"Test extract_fields function."""
    repo_id = '0'
    rec_type = 'resource'
    field = 'publish'
    with requests_mock.Mocker() as m:
        all_ids = [1]
        m.get('/repositories/0/resources?all_ids=true', json=all_ids)
        res_1 = {'title': 'Title', 'publish': True}
        m.get('/repositories/0/resources/1', json=res_1)
        models.extract_fields(as_ops, repo_id, rec_type, field)
        message = json.loads(caplog.messages[1])
        assert message['uri'] == 'repositories/0/resources/1'
        assert message['publish'] is True


def test_extract_note_field(caplog):
    """"Test extract_note_field function."""
    field = 'acqinfo'
    rec_obj = {'notes': [{'type': 'acqinfo', 'subnotes': [{'content':
               'test value'}]}]}
    report_dict = {'uri': '123', 'title': 'Title', 'id': '456'}
    models.extract_note_field(field, rec_obj, report_dict)
    message = json.loads(caplog.messages[0])
    assert message['uri'] == '123'
    assert message['acqinfo'] == 'test value'


def test_extract_obj_field(caplog):
    """"Test extract_obj_field function."""
    field = 'dates'
    rec_obj = {'dates': [{'begin': '1900', 'end': '1901', 'date_type':
               'inclusive'}]}
    report_dict = {'uri': '123', 'title': 'Title', 'id': '456'}
    obj_field_dict = {'dates': ['begin', 'end', 'expression', 'label',
                      'date_type']}
    models.extract_obj_field(field, rec_obj, obj_field_dict, report_dict)
    message = json.loads(caplog.messages[0])
    assert message['uri'] == '123'
    assert message['begin'] == '1900'
    assert message['end'] == '1901'
    assert message['date_type'] == 'inclusive'


def test_concat_id():
    """"Test concat_id function."""
    rec_obj = {'id_0': '1', 'id_1': '2', 'id_2': '3', 'id_3': '4'}
    coll_id = models.concat_id(rec_obj)
    assert coll_id == '1-2-3-4'


def test_download_json():
    """Test download_json function."""
    rec_obj = models.Record()
    rec_obj['uri'] = '/test/123'
    path = models.download_json(rec_obj)
    assert os.path.isfile(path)
    os.remove(path)


# How to test this?
# def test_create_csv_from_log():
#   """"Test create_csv_from_log function."""
#     assert False


def test_audit():
    """"Test audit function."""
    sample_record = {'uri': '123'}
    change = {'op': 'add', 'path': '/title', 'value': 'I am a title'}
    msg = models.audit(record=sample_record, **change)
    assert msg == {'uri': '123', 'field': '/title', 'old': None,
                   'new': 'I am a title'}


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
