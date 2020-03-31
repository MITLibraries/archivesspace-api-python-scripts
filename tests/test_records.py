from asaps import records


def test_create_arch_obj():
    """Test create_arch_obj method."""
    title = 'Test title'
    level = 'series'
    notes = []
    agents = [{'ref': '/agents/123'}]
    parent = '/repositories/0/archival_objects/123'
    resource = '/repositories/0/resources/456'
    arch_obj = records.create_arch_obj(title, level, agents, notes,
                                       parent, resource)
    assert arch_obj['title'] == title
    assert arch_obj['level'] == level
    assert arch_obj['linked_agents'] == agents
    assert arch_obj['parent']['ref'] == parent
    assert arch_obj['resource']['ref'] == resource


def test_create_dig_obj():
    """Test create_dig_obj method."""
    title = 'Test title'
    link = '/repositories/0/digital_objects/123'
    dig_obj = records.create_dig_obj(title, link)
    assert dig_obj['title'] == title
    assert dig_obj['digital_object_id'] == link


def test_create_note():
    """Test create_note method."""
    content = 'Test content'
    label = 'Scope and Content Note'
    type = 'scopecontent'
    note = records.create_note(type, label, content)
    assert note['label'] == label
    assert note['subnotes'][0]['content'] == content
    assert note['type'] == type


def test_link_dig_obj():
    """Test link_dig_obj method."""
    arch_obj = {'instances': []}
    dig_obj_uri = '/repositories/0/digital_objects/123'
    arch_obj = records.link_dig_obj(arch_obj, dig_obj_uri)
    assert arch_obj['instances'][0]['digital_object']['ref'] == dig_obj_uri


def test_link_top_container():
    """Test link_top_container method."""
    arch_obj = {'instances': []}
    top_cont_uri = '/repositories/0/top_containers/123'
    child_type = 'barrel'
    child_indicator = '1'
    arch_obj = records.link_top_container(arch_obj, top_cont_uri, child_type,
                                          child_indicator)
    assert (arch_obj['instances'][0]['sub_container']['top_container']
            ['ref']) == top_cont_uri


def test_update_dig_obj_link():
    """Test update_dig_obj_link method."""
    update = 'TEST'
    do = {'digital_object_id': 'fish', 'file_versions': [{'file_uri':
          'fish'}]}
    do = records.update_dig_obj_link(do, update)
    assert do['digital_object_id'] == update
    for file_version in do['file_versions']:
        assert file_version['file_uri'] == update
