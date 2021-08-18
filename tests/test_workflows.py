import json
import logging

from asaps import workflows


def test_create_new_digital_objects(as_ops, caplog, runner):
    caplog.set_level(logging.INFO)
    workflows.create_new_digital_objects(as_ops, "tests/fixtures/newdigobjs.csv", "0")
    message_1 = json.loads(caplog.messages[1])["event"]
    message_2 = json.loads(caplog.messages[2])["event"]
    assert message_1["uri"] == "/repositories/0/digital_objects/5678"
    assert message_2["post"] == "Success"


def test_export_metadata(as_ops):
    report_dicts = workflows.export_metadata(as_ops, "423", "ref_id", "0")
    for report_dict in report_dicts:
        assert report_dict["uri"] == "/repositories/0/archival_objects/1234"
        assert report_dict["title"] == "Sample Title"
        assert report_dict["file_identifier"] == "a2b2c2"
