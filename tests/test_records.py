from asaps import records


def test_create_agent_pers():
    agent_type = "agent_person"
    primary_name = "Smith"
    sort_name = "Smith, John, 1902-2049"
    authority_id = "mock://mock.mock/123"
    rest_of_name = "John"
    fuller_form = ""
    title = ""
    prefix = ""
    suffix = ""
    dates = "1902-2049"
    expression = ""
    begin = "1902"
    end = "2049"
    certainty = ""
    label = "existence"
    agent_record = records.create_agent_pers(
        agent_type,
        primary_name,
        sort_name,
        rest_of_name,
        fuller_form,
        title,
        prefix,
        suffix,
        dates,
        expression,
        begin,
        end,
        authority_id,
        certainty,
        label,
    )
    assert agent_record["names"][0]["primary_name"] == primary_name
    assert agent_record["names"][0]["sort_name"] == sort_name
    assert agent_record["names"][0]["authority_id"] == authority_id
    assert agent_record["names"][0]["rest_of_name"] == rest_of_name
    assert agent_record["names"][0]["dates"] == dates
    assert agent_record["dates_of_existence"][0]["begin"] == begin
    assert agent_record["dates_of_existence"][0]["end"] == end


def test_create_agent_corp():
    agent_type = "agent_corporate_entity"
    primary_name = "Company"
    sort_name = "Company. That Does. Stuff"
    authority_id = "mock://mock.mock/456"
    subord_name_1 = "That Does"
    subord_name_2 = "Stuff"
    number = ""
    qualifier = ""
    dates = ""
    agent_record = records.create_agent_corp(
        agent_type,
        primary_name,
        sort_name,
        subord_name_1,
        subord_name_2,
        number,
        dates,
        qualifier,
        authority_id,
    )
    assert agent_record["names"][0]["primary_name"] == primary_name
    assert agent_record["names"][0]["sort_name"] == sort_name
    assert agent_record["names"][0]["authority_id"] == authority_id
    assert agent_record["names"][0]["subordinate_name_1"] == subord_name_1
    assert agent_record["names"][0]["subordinate_name_2"] == subord_name_2


def test_create_archival_object():
    title = "Test title"
    level = "series"
    notes = []
    agents = [{"ref": "/agents/123"}]
    parent = "/repositories/0/archival_objects/123"
    resource = "/repositories/0/resources/456"
    begin = "1900"
    end = "2020"
    expression = ""
    certainty = ""
    label = "creation"
    archival_object = records.create_archival_object(
        title,
        level,
        agents,
        notes,
        parent,
        resource,
        begin,
        end,
        expression,
        certainty,
        label,
    )
    assert archival_object["title"] == title
    assert archival_object["level"] == level
    assert archival_object["linked_agents"] == agents
    assert archival_object["parent"]["ref"] == parent
    assert archival_object["resource"]["ref"] == resource
    assert archival_object["dates"][0]["begin"] == begin
    assert archival_object["dates"][0]["end"] == end
    assert archival_object["dates"][0]["label"] == label


def test_create_date():
    expression = ""
    begin = "1902"
    end = "2049"
    certainty = ""
    label = "existence"
    date = records.create_date(begin, end, expression, certainty, label)
    assert date["begin"] == begin
    assert date["end"] == end
    assert date["label"] == label


def test_create_digital_object():
    title = "Test title"
    link = "/repositories/0/digital_objects/123"
    digital_object = records.create_digital_object(title, link)
    assert digital_object["title"] == title
    assert digital_object["digital_object_id"] == link


def test_create_note():
    content = "Test content"
    label = "Scope and Content Note"
    type = "scopecontent"
    note = records.create_note(type, label, content)
    assert note["label"] == label
    assert note["subnotes"][0]["content"] == content
    assert note["type"] == type


def test_link_digital_object():
    archival_object = {"instances": []}
    digital_object_uri = "/repositories/0/digital_objects/123"
    archival_object = records.link_digital_object(archival_object, digital_object_uri)
    assert (
        archival_object["instances"][0]["digital_object"]["ref"] == digital_object_uri
    )


def test_link_top_container():
    archival_object = {"instances": []}
    top_container_uri = "/repositories/0/top_containers/123"
    child_type = "barrel"
    child_indicator = "1"
    archival_object = records.link_top_container(
        archival_object, top_container_uri, child_type, child_indicator
    )
    assert (
        archival_object["instances"][0]["sub_container"]["top_container"]["ref"]
    ) == top_container_uri


def test_update_digital_object_link():

    update = "TEST"
    digital_object = {
        "digital_object_id": "fish",
        "file_versions": [{"file_uri": "fish"}],
    }
    digital_object = records.update_digital_object_link(digital_object, update)
    assert digital_object["digital_object_id"] == update
    for file_version in digital_object["file_versions"]:
        assert file_version["file_uri"] == update
