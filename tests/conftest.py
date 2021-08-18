import logging

import pytest
import requests_mock
import structlog
from asnake.client import ASnakeClient
from click.testing import CliRunner

from asaps import models


@pytest.fixture(autouse=True)
def as_mock():
    with requests_mock.Mocker() as m:
        ids_json = [423, 756]
        m.get("/repositories/0/resources?all_ids=true", json=ids_json)
        resource_json_1 = {
            "jsonmodel_type": "resource",
            "id_0": "AB",
            "id_1": "123",
            "title": "Test title 1",
            "uri": "/repositories/0/resources/423",
            "ref_id": "a1b_2c3",
            "notes": [{"type": "acqinfo", "subnotes": [{"content": "test value"}]}],
        }
        m.get("/repositories/0/resources/423", json=resource_json_1)
        resource_json_2 = {
            "jsonmodel_type": "resource",
            "uri": "/repositories/0/resources/756",
            "title": "Test title 2",
            "notes": [],
        }
        m.get("/repositories/0/resources/756", json=resource_json_2)
        resource_updated_json = {"post": "Success"}
        m.post("/repositories/0/resources/423", json=resource_updated_json)
        tree_json = {
            "record_uri": "/repositories/0/archival_objects/1234",
            "children": [{"record_uri": "/repositories/0/archival_objects/5678"}],
        }
        m.get("/repositories/2/resources/423/tree", json=tree_json)
        resource_created_json = {"status": "Created"}
        m.post("/repositories/0/resources", json=resource_created_json)
        search_json = [{"uri": "/repositories/0/archival_objects/1234"}]
        m.get("/repositories/0/search?", json=search_json)
        tree_json = {"record_uri": "/repositories/0/archival_objects/1234"}
        m.get("/repositories/0/resources/423/tree", json=tree_json)
        archival_object_json = {
            "uri": "/repositories/0/archival_objects/1234",
            "ref_id": "a2b2c2",
            "display_string": "Sample Title",
            "instances": [],
            "notes": [{"type": "acqinfo", "subnotes": [{"content": "test value"}]}],
        }
        m.get("/repositories/0/archival_objects/1234", json=archival_object_json)
        archival_object_updated_json = {"post": "Success"}
        m.post(
            "/repositories/0/archival_objects/1234", json=archival_object_updated_json
        )
        digital_object_created_json = {
            "post": "Success",
            "uri": "/repositories/0/digital_objects/5678",
        }
        m.post("/repositories/0/digital_objects", json=digital_object_created_json)
        agent_created_json = {"status": "Created", "uri": "/agents/people/789"}
        m.post("/agents/people", json=agent_created_json)
        archival_object_created_json = {
            "status": "Created",
            "uri": "/repositories/0/archival_objects/123",
        }
        m.post("/repositories/0/archival_objects", json=archival_object_created_json)
        digital_object_json = {
            "file_versions": [{}],
            "uri": "/repositories/0/digital_objects/5678",
        }
        m.get("/repositories/0/digital_objects/5678", json=digital_object_json)
        digital_object_updated_json = {"post": "Success"}
        m.post("/repositories/0/digital_objects/5678", json=digital_object_updated_json)
        yield m


@pytest.fixture
def as_ops():
    client = ASnakeClient(
        baseurl="mock://example.com", username="test", password="test"
    )
    as_ops = models.AsOperations(client)
    return as_ops


@pytest.fixture(autouse=True, scope="session")
def logger():
    logger = structlog.get_logger()
    logging.basicConfig(
        format="%(message)s", handlers=[logging.StreamHandler()], level=logging.INFO
    )
    return logger


@pytest.fixture()
def output_dir(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(f"{output_dir}/")


@pytest.fixture(autouse=True)
def runner():
    return CliRunner()
