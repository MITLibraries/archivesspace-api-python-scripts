import requests_mock
from asaps import models
from asnake.client import ASnakeClient
import pytest


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
        assert response.json_string == json_object


def test_record_is_modified():
    record = models.Resource()
    assert not record.modified
    record.title = "I am different"
    assert record.modified


# def test_search(as_ops):
#     """Test search method."""
#     assert False
#
#
# def test_post_record(as_ops):
#     """Test post_record method."""
#     assert False
#
#
# def test__pop_inst():
#     """Test _pop_inst method."""
#     assert False
#
#
# def test_download_json():
#     """Test download_json function."""
#     assert False
#
#
# def test_create_csv():
#     """Test create_csv function."""
#     assert False
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
