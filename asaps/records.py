def create_arch_obj(title, level, agents, notes, parent, resource):
    """Create archival object."""
    arch_obj = {}
    arch_obj['title'] = title
    arch_obj['level'] = level
    arch_obj['linked_agents'] = agents
    arch_obj['notes'] = notes
    arch_obj['publish'] = True
    arch_obj['parent'] = {'ref': parent}
    arch_obj['resource'] = {'ref': resource}
    arch_obj['instances'] = []
    return arch_obj


def create_dig_obj(title, link):
    """Create digital object."""
    dig_obj = {}
    dig_obj['title'] = title
    dig_obj['publish'] = True
    dig_obj['file_versions'] = []
    dig_obj = update_dig_obj_link(dig_obj, link)
    return dig_obj


def create_note(type, label, content):
    """Create note object."""
    note = {}
    note['jsonmodel_type'] = 'note_multipart'
    note['type'] = type
    note['label'] = label
    note['publish'] = True
    subnote = {}
    subnote['publish'] = True
    subnote['content'] = content
    subnote['jsonmodel_type'] = 'note_text'
    note['subnotes'] = [subnote]
    return note


def link_dig_obj(arch_obj, dig_obj_uri):
    """Link digital object to archival object."""
    instance = {}
    instance['instance_type'] = 'digital_object'
    instance['jsonmodel_type'] = 'instance'
    instance['digital_object'] = {'ref': dig_obj_uri}
    instance['is_representative'] = True
    arch_obj['instances'].append(instance)
    return arch_obj


def link_top_container(arch_obj, top_cont_uri, child_type,
                       child_indicator):
    """Link top container to archival object."""
    instance = {}
    instance['instance_type'] = 'mixed_materials'
    instance['jsonmodel_type'] = 'instance'
    instance['indicator_2'] = child_indicator
    instance['type_2'] = child_type
    sub_container = {}
    sub_container['indicator_2'] = child_indicator
    sub_container['type_2'] = child_type
    sub_container['jsonmodel_type'] = 'sub_container'
    sub_container['top_container'] = {'ref': top_cont_uri}
    instance['sub_container'] = sub_container
    instance['is_representative'] = False
    arch_obj['instances'].append(instance)
    return arch_obj


def update_dig_obj_link(dig_obj, link):
    """Get digital objects associated with an archival objects."""
    dig_obj['digital_object_id'] = link
    if len(dig_obj['file_versions']) != 0:
        for file_version in dig_obj['file_versions']:
            file_version['file_uri'] = link
    else:
        file_version = {}
        file_version['file_uri'] = link
        file_version['publish'] = True
        file_version['is_representative'] = True
        file_version['jsonmodel_type'] = 'file_version'
        dig_obj['file_versions'] = [file_version]
    return dig_obj
