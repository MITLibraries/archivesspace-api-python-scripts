import copy
import csv
import datetime
import json
import logging
import os
import time

import jsonpatch
import jsonpointer
import structlog

logger = structlog.get_logger()
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
log_file_name = f'log-{timestamp}.log'
logging.basicConfig(format="%(message)s",
                    handlers=[logging.FileHandler(log_file_name, 'w'),
                              logging.StreamHandler()], level=logging.INFO)
logger.info('Application start')


class AsOperations:
    def __init__(self, client):
        """Create instance and import client as attribute."""
        self.client = client

    def get_record(self, uri):
        """Retrieve an individual record."""
        record = self.client.get(uri).json()
        logger.info(uri)
        return Record(record)

    def create_endpoint(self, rec_type, repo_id):
        """Create an endpoint for a specified type."""
        rec_type_dict = {'accession': 'accessions', 'resource': 'resources',
                         'archival_object': 'archival_objects,',
                         'agent_corporate_entity': 'corporate_entities',
                         'agent_person': 'people', 'agent_family': 'families',
                         'top_container': 'top_containers'}
        agents = ['corporate_entities', 'families', 'people']
        non_repo_types = ['locations', 'subjects']
        if rec_type in agents:
            endpoint = f'agents/{rec_type}'
        elif rec_type in non_repo_types:
            endpoint = rec_type
        else:
            endpoint = (f'repositories/{repo_id}/{rec_type_dict[rec_type]}')
        return endpoint

    def get_all_records(self, endpoint):
        """Retrieve all records from a specified endpoint."""
        ids = self.client.get(f'{endpoint}?all_ids=true').json()
        return ids

    def search(self, string, repo_id, rec_type, note_type='keyword'):
        """Search for a string across a particular record type."""
        endpoint = f'repositories/{repo_id}/search?'
        query = {'query': {'field': note_type, 'value': string,
                 'jsonmodel_type': 'field_query'}}
        params = {'aq': json.dumps(query), 'page_size': 100,
                  'type[]': rec_type}
        uris = []
        for result in self.client.get_paged(endpoint, params=params):
            uri = result['uri']
            uris.append(uri)
        logger.info('Search results processed')
        return uris

    def save_record(self, rec_obj, dry_run):
        """Update ArchivesSpace record with POST of JSON data."""
        if dry_run == 'False':
            response = self.client.post(rec_obj['uri'], json=rec_obj)
            response.raise_for_status()
            logger.info(response.json())
        rec_obj.flush()

    def get_aos_for_resource(self, uri):
        """Get archival objects associated with a resource."""
        logger.info(f'Retrieving AOs for {uri}')
        aolist = []
        output = self.client.get(f'{uri}/tree').json()
        for ao_uri in find_key(output, 'record_uri'):
            if 'archival_objects' in ao_uri:
                aolist.append(ao_uri)
        return aolist

    def extract_fields(self, repo_id, rec_type, field):
        """Extract field (list or string value) from a type of records."""
        endpoint = self.create_endpoint(rec_type, repo_id)
        ids = self.get_all_records(endpoint)
        for id in ids:
            uri = f'{endpoint}/{id}'
            rec_obj = self.get_record(uri)
            coll_id = concat_id(rec_obj)
            report_dict = {'uri': uri, 'title': rec_obj['title'],
                           'id': coll_id}
            obj_field_dict = {'dates': ['begin', 'end', 'expression', 'label',
                              'date_type'],
                              'extents': ['portion', 'number', 'extent_type',
                                          'container_summary',
                                          'physical_details', 'dimensions']}
            note_type_fields = ['bioghist', 'accessrestrict', 'userestrict',
                                'prefercite', 'altformavail',
                                'relatedmaterial', 'acqinfo', 'arrangement',
                                'processinfo', 'bibliography']
            if field in note_type_fields:
                self.extract_note_field(field, rec_obj, report_dict)
            elif field in obj_field_dict.keys():
                self.extract_obj_field(field, rec_obj, obj_field_dict,
                                       report_dict)
            else:
                report_dict[field] = rec_obj.get(field, '')
                logger.info(**report_dict)

    def extract_note_field(self, field, rec_obj, report_dict):
        """Extract note field content."""
        notes = filter_note_type(rec_obj, field)
        for note in notes:
            for subnote in note.get('subnotes', []):
                print(subnote)
                report_dict[field] = subnote['content']
                logger.info(**report_dict)

    def extract_obj_field(self, field, rec_obj, obj_field_dict,
                          report_dict):
        """Extract field content where the value is an object."""
        keys = obj_field_dict[field]
        object_list = rec_obj[field]
        for object in object_list:
            for key in keys:
                report_dict[key] = object.get(key, '')
            logger.info(**report_dict)


class Record(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__persisted = copy.deepcopy(self)

    def flush(self):
        for change in self.changes:
            logger.info(**audit(record=self.__persisted, **change))
        self.__persisted = copy.deepcopy(self)

    @property
    def changes(self):
        return list(jsonpatch.make_patch(self.__persisted, self))

    @property
    def modified(self):
        return bool(self.changes)


def audit(**kwargs):
    """Create audit message."""
    record = kwargs['record']
    op = kwargs['op']
    path = kwargs['path']

    uri = record.get('uri')
    if op == 'add':
        new = kwargs.get('value')
        msg = {'uri': uri, 'field': path, 'old': None, 'new': new}
    elif op == 'replace':
        old = jsonpointer.resolve_pointer(record, path)
        new = kwargs.get('value')
        msg = {'uri': uri, 'field': path, 'old': old, 'new': new}
    elif op == 'remove':
        old = jsonpointer.resolve_pointer(record, path)
        msg = {'uri': uri, 'field': path, 'old': old, 'new': None}
    else:
        msg = {}
    return msg


def concat_id(rec_obj):
    """Retrieve URI and concatenated IDs for record."""
    id_0 = rec_obj.get('id_0', '')
    id_1 = rec_obj.get('id_1', '')
    id_2 = rec_obj.get('id_2', '')
    id_3 = rec_obj.get('id_3', '')
    coll_id = id_0
    if id_1 != '':
        coll_id += f'-{id_1}'
        if id_2 != '':
            coll_id += f'-{id_2}'
            if id_3 != '':
                coll_id += f'-{id_3}'
    return coll_id


def download_json(rec_obj):
    """Download a JSON file."""
    uri = rec_obj['uri']
    file_name = uri[1:len(uri)].replace('/', '-')
    f = open(file_name + '.json', 'w')
    json.dump(rec_obj, f)
    f.close()
    return f.name


def create_csv_from_log():
    """Create csv from log file."""
    with open(log_file_name) as f:
        logs = f.read().splitlines()
        edit_log_lines = []
        for line in logs:
            line_dict = json.loads(line)
            if 'uri' in line_dict.keys():
                line_dict.pop('logger')
                line_dict.pop('level')
                line_dict.pop('timestamp')
                edit_log_lines.append(line_dict)
    full_file_name = os.path.abspath(f'{log_file_name}.csv')
    if len(edit_log_lines) > 0:
        with open(f'{full_file_name}', 'w') as fp:
            header = list(edit_log_lines[0].keys())
            f = csv.DictWriter(fp, fieldnames=header)
            f.writeheader()
            for edit_log_line in edit_log_lines:
                f.writerow(edit_log_line)


def filter_note_type(rec_obj, note_type):
    """Filter notes by type."""
    return (n for n in rec_obj['notes'] if n.get('type') == note_type)


def find_key(nest_dict, key):
    """Find all instances of a key in a nested dictionary."""
    if key in nest_dict:
        yield nest_dict[key]
    children = nest_dict.get('children')
    if isinstance(children, list):
        for child in children:
            yield from find_key(child, key)


def elapsed_time(start_time, label):
    """Calculate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - start_time)
    logger.info(f'{label} : {td}')
