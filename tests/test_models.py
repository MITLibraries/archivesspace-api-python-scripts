import requests_mock
from asaps import models
from asnake.client import ASnakeClient
import pytest
import os


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


def test_record_is_modified():
    record = models.Record()
    assert not record.modified
    record['title'] = "I am different"
    assert record.modified


def test_search(as_ops):
    """Test search method."""
    with requests_mock.Mocker() as m:
        string = 'string'
        repo_id = '2'
        rec_type = 'resource'
        json_object = [{'uri': '1234'}]
        url = f'mock://example.com/repositories/2/search?q="{string}'
        url += f'"&page_size=100&type[]={rec_type}'
        m.get(url, json=json_object)
        response = as_ops.search(string, repo_id, rec_type)
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
    cwd = os.getcwd()
    path = os.path.join(cwd, full_file_name)
    assert os.path.isfile(path)
    os.remove(path)
#
#
# def test_filter_note_type():
#     """Test filter_note_type function."""
#     assert False
#
#
# def test_replace_str():
#     """Test replace_str function."""
#     assert False
#
#
# def test_update_record():
#     """Test update_record function."""
#     assert False
#
#
# def test_find_key():
#     """Test find_key function."""
#     assert False
#
#
# def test_get_aos_for_resource():
#     """Test get_aos_for_resource function."""
#     assert False
