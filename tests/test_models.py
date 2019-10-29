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
        response = as_ops.search(string, repo_id, rec_type, note_type)
        for result in response:
            assert result == json_object[0]


def test_save_record(as_ops):
    """Test post_record method."""
    with requests_mock.Mocker() as m:
        rec_obj = models.Record()
        uri = '/repositories/2/resources/423'
        rec_obj['uri'] = uri
        json_object = {'post': 'Success'}
        m.post(uri, json=json_object)
        response = as_ops.save_record(rec_obj)
        assert response == json_object


def test_save_record_flushes_changes(as_ops):
    with requests_mock.Mocker() as m:
        uri = '/foo/bar/1'
        m.post(uri, json={'post': 'Success'})
        r = models.Record({'uri': uri})
        r['title'] = 'A title'
        assert r.modified
        as_ops.save_record(r)
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


def test_download_json(as_ops):
    """Test download_json function."""
    rec_obj = models.Record()
    rec_obj['uri'] = '/test/123'
    path = models.download_json(rec_obj)
    assert os.path.isfile(path)
    os.remove(path)


def test_create_csv(as_ops):
    """Test create_csv function."""
    csv_data = [{'test1': '1', 'test2': '2'}]
    file_name = 'test'
    full_file_name = models.create_csv(csv_data, file_name)
    assert os.path.isfile(full_file_name)
    os.remove(full_file_name)


def test_filter_note_type():
    """Test filter_note_type function."""
    rec_obj = {'notes': [{'note_type': 'acqinfo'}, {'note_type': 'bioghist'}]}
    notes = models.filter_note_type(rec_obj, 'acqinfo')
    for note in notes:
        assert note['note_type'] == 'acqinfo'


def test_replace_str():
    """Test replace_str function."""
    csv_row = {'old_values': [], 'new_values': []}
    note = {'content': 'The dog jumped.'}
    csv_row = models.replace_str(csv_row, note, 'dog', 'cow')
    assert csv_row['old_values'] == ['The dog jumped.']
    assert csv_row['new_values'] == ['The cow jumped.']


def test_find_key():
    """Test find_key function."""
    nest_dict = {'children': [{'publish': True, 'children': [{'publish':
                 True}]}]}
    keys = models.find_key(nest_dict, 'children')
    key_count = 0
    for key in keys:
        key_count += 1
    assert key_count == 2
