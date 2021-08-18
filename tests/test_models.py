import csv
import json
import logging
import os

import pytest
from asnake.client import ASnakeClient

from asaps import models


@pytest.fixture
def as_ops():
    client = ASnakeClient(
        baseurl="mock://example.com", username="test", password="test"
    )
    as_ops = models.AsOperations(client)
    return as_ops


def test_get_all_records(as_ops):
    endpoint = "/repositories/0/resources"
    ids = as_ops.get_all_records(endpoint)
    assert ids == [423, 756]


def test_get_archival_objects_for_resource(as_ops):
    resource = "/repositories/2/resources/423"
    archival_object_list = as_ops.get_archival_objects_for_resource(resource)
    assert "/repositories/0/archival_objects/5678" in archival_object_list
    assert "/repositories/0/archival_objects/1234" in archival_object_list


def test_get_record(as_ops):
    uri = "/repositories/0/resources/423"
    response = as_ops.get_record(uri)
    assert response["jsonmodel_type"] == "resource"


def test_post_new_record(as_ops):
    endpoint = "/repositories/0/resources"
    record_object = {"title": "Test title"}
    response = as_ops.post_new_record(record_object, endpoint)
    assert response["status"] == "Created"


def test_save_record(as_ops, caplog):
    caplog.set_level(logging.INFO)
    record_object = models.Record()
    uri = "/repositories/0/resources/423"
    record_object["uri"] = uri
    as_ops.save_record(record_object, True)
    message = json.loads(caplog.messages[0])["event"]
    assert message == {"post": "Success"}


def test_search(as_ops):
    string = "string"
    repository_id = "0"
    record_type = "resource"
    field = "acqinfo"
    results = as_ops.search(string, repository_id, record_type, field)
    for result in results:
        assert result == "/repositories/0/archival_objects/1234"


def test_record_is_modified():
    record = models.Record()
    assert not record.modified
    record["title"] = "I am different"
    assert record.modified


def test_record_flush_persists_changes():
    record = models.Record()
    record["title"] = "I am a title"
    assert record.modified
    record.flush()
    assert not record.modified


def test_changes_returns_json_patch_operations():
    record = models.Record()
    record["title"] = "I am a title"
    assert record.changes == [{"op": "add", "path": "/title", "value": "I am a title"}]


def test_save_record_flushes_changes(as_ops):
    uri = "/repositories/0/resources/423"
    record = models.Record({"uri": uri})
    record["title"] = "A title"
    assert record.modified
    as_ops.save_record(record, True)
    assert not record.modified


def test_audit():
    sample_record = {"uri": "123"}
    change = {"op": "add", "path": "/title", "value": "I am a title"}
    message = models.audit(record=sample_record, **change)
    assert message == {
        "uri": "123",
        "field": "/title",
        "old": None,
        "new": "I am a title",
    }


def test_concat_id():
    record_object = {"id_0": "1", "id_1": "2", "id_2": "3", "id_3": "4"}
    collection_id = models.concat_id(record_object)
    assert collection_id == "1-2-3-4"


def test_create_endpoint():
    record_type = "resource"
    repository_id = "0"
    endpoint = models.create_endpoint(record_type, repository_id)
    assert endpoint == "repositories/0/resources"


def test_create_csv_from_log(runner):
    with runner.isolated_filesystem():
        os.mkdir("logs")
        with open("logs/log-1790-01-01.log", "w") as log_file:
            log_data = json.dumps(
                {
                    "uri": "/repositories/0/events/123",
                    "event_type": "processed",
                    "date": "1861-04-10",
                    "logger": "asaps.cli",
                    "level": "info",
                    "timestamp": "2021-03-04T15:21:28.616824Z",
                }
            )
            log_file.write(log_data)
        models.create_csv_from_log("test-", "1790-01-01.log", True)
        with open("test-1790-01-01.log.csv") as csvfile2:
            reader = csv.DictReader(csvfile2)
            for row in reader:
                assert row["uri"] == "/repositories/0/events/123"
                assert row["event_type"] == "processed"
                assert row["date"] == "1861-04-10"


def test_download_json():
    record_object = models.Record()
    record_object["uri"] = "/test/123"
    path = models.download_json(record_object)
    assert os.path.isfile(path)
    os.remove(path)


def test_extract_note_field():
    field = "acqinfo"
    record_object = {
        "notes": [{"type": "acqinfo", "subnotes": [{"content": "test value"}]}]
    }
    report_dict = {"uri": "123", "title": "Title", "id": "456"}
    report_dicts = models.extract_note_field(field, record_object, report_dict)
    for report_dict in report_dicts:
        assert report_dict["uri"] == "123"
        assert report_dict["acqinfo"] == "test value"


def test_extract_obj_field():
    field = "dates"
    record_object = {
        "dates": [{"begin": "1900", "end": "1901", "date_type": "inclusive"}]
    }
    report_dict = {"uri": "123", "title": "Title", "id": "456"}
    object_field_dict = {"dates": ["begin", "end", "expression", "label", "date_type"]}
    report_dicts = models.extract_obj_field(
        field, record_object, object_field_dict, report_dict
    )
    for report_dict in report_dicts:
        assert report_dict["uri"] == "123"
        assert report_dict["begin"] == "1900"
        assert report_dict["end"] == "1901"
        assert report_dict["date_type"] == "inclusive"


def test_filter_note_type():
    record_object = {"notes": [{"note_type": "acqinfo"}, {"note_type": "bioghist"}]}
    notes = models.filter_note_type(record_object, "acqinfo")
    for note in notes:
        assert note["note_type"] == "acqinfo"


def test_find_key():
    nested_dict = {"children": [{"publish": True, "children": [{"publish": True}]}]}
    keys = models.find_key(nested_dict, "children")
    key_count = 0
    for key in keys:
        key_count += 1
    assert key_count == 2


def test_string_to_uri():
    agent_links = []
    string = "Smith, N."
    uri_dict = {"Smith, N.": "mock.mock/123"}
    role = "creator"
    agent_links = models.string_to_uri(agent_links, string, uri_dict, role, "")
    assert agent_links[0]["ref"] == uri_dict[string]
    assert agent_links[0]["role"] == role
