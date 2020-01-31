import requests

NS = {'oai': 'http://www.openarchives.org/OAI/2.0/',
      'atom': 'http://www.w3.org/2005/Atom'}


def get_bitstreams(item, file_type, namespace):
    """"Retrieves the bitstreams of the specified item."""
    for element in item.iterfind('.//atom:link', namespace):
        if element.attrib.get('type') == file_type:
            yield element.attrib['href']


def extract_handle(item, namespace):
    """"Retrieves the bitstreams of the specified item."""
    handle = ''
    handle = item.find('.//atom:link[@rel="alternate"]',
                       namespaces=namespace)
    if handle is not None:
        handle = handle.attrib['href']
    return handle


def post_parameters(target_url, metadata_system, source_system, handle, title,
                    bitstream_array):
    """"Posts parameters to API endpoint."""
    params = {}
    params['metadata_system'] = metadata_system
    params['source_system'] = source_system
    params['handle'] = handle
    params['title'] = title
    params['target_links'] = bitstream_array
    print(params)
    # Will add to header as authentication method becomes clearer
    header = {}
    id = requests.post(target_url, headers=header, params=params).json()
    dig_obj = requests.get(f'{target_url}?oid={id}', headers=header,
                           params=params).json()
    links = dig_obj.get('files')
    if links is not None:
        for link in links:
            yield link['path']
