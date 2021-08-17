from asaps import records


def test_create_agent_pers():
    """Test create_agent_pers function."""
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
    agent_rec = records.create_agent_pers(
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
    assert agent_rec["names"][0]["primary_name"] == primary_name
    assert agent_rec["names"][0]["sort_name"] == sort_name
    assert agent_rec["names"][0]["authority_id"] == authority_id
    assert agent_rec["names"][0]["rest_of_name"] == rest_of_name
    assert agent_rec["names"][0]["dates"] == dates
    assert agent_rec["dates_of_existence"][0]["begin"] == begin
    assert agent_rec["dates_of_existence"][0]["end"] == end


def test_create_agent_corp():
    """Test create_agent_corp function."""
    agent_type = "agent_corporate_entity"
    primary_name = "Company"
    sort_name = "Company. That Does. Stuff"
    authority_id = "mock://mock.mock/456"
    subord_name_1 = "That Does"
    subord_name_2 = "Stuff"
    number = ""
    qualifier = ""
    dates = ""
    agent_rec = records.create_agent_corp(
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
    assert agent_rec["names"][0]["primary_name"] == primary_name
    assert agent_rec["names"][0]["sort_name"] == sort_name
    assert agent_rec["names"][0]["authority_id"] == authority_id
    assert agent_rec["names"][0]["subordinate_name_1"] == subord_name_1
    assert agent_rec["names"][0]["subordinate_name_2"] == subord_name_2


def test_create_arch_obj():
    """Test create_arch_obj function."""
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
    arch_obj = records.create_arch_obj(
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
    assert arch_obj["title"] == title
    assert arch_obj["level"] == level
    assert arch_obj["linked_agents"] == agents
    assert arch_obj["parent"]["ref"] == parent
    assert arch_obj["resource"]["ref"] == resource
    assert arch_obj["dates"][0]["begin"] == begin
    assert arch_obj["dates"][0]["end"] == end
    assert arch_obj["dates"][0]["label"] == label


def test_create_date():
    """Test create_date function."""
    expression = ""
    begin = "1902"
    end = "2049"
    certainty = ""
    label = "existence"
    date = records.create_date(begin, end, expression, certainty, label)
    assert date["begin"] == begin
    assert date["end"] == end
    assert date["label"] == label


def test_create_dig_obj():
    """Test create_dig_obj method."""
    title = "Test title"
    link = "/repositories/0/digital_objects/123"
    dig_obj = records.create_dig_obj(title, link)
    assert dig_obj["title"] == title
    assert dig_obj["digital_object_id"] == link


def test_create_note():
    """Test create_note method."""
    content = "Test content"
    label = "Scope and Content Note"
    type = "scopecontent"
    note = records.create_note(type, label, content)
    assert note["label"] == label
    assert note["subnotes"][0]["content"] == content
    assert note["type"] == type


def test_link_dig_obj():
    """Test link_dig_obj method."""
    arch_obj = {"instances": []}
    dig_obj_uri = "/repositories/0/digital_objects/123"
    arch_obj = records.link_dig_obj(arch_obj, dig_obj_uri)
    assert arch_obj["instances"][0]["digital_object"]["ref"] == dig_obj_uri


def test_link_top_container():
    """Test link_top_container method."""
    arch_obj = {"instances": []}
    top_cont_uri = "/repositories/0/top_containers/123"
    child_type = "barrel"
    child_indicator = "1"
    arch_obj = records.link_top_container(
        arch_obj, top_cont_uri, child_type, child_indicator
    )
    assert (
        arch_obj["instances"][0]["sub_container"]["top_container"]["ref"]
    ) == top_cont_uri


def test_update_dig_obj_link():
    """Test update_dig_obj_link method."""
    update = "TEST"
    do = {"digital_object_id": "fish", "file_versions": [{"file_uri": "fish"}]}
    do = records.update_dig_obj_link(do, update)
    assert do["digital_object_id"] == update
    for file_version in do["file_versions"]:
        assert file_version["file_uri"] == update
