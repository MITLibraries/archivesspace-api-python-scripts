import copy
import csv
import datetime
from functools import partial
import json
import logging
import logging.config
import operator
import os
import time

import attr
import jsonpatch
import jsonpointer


op = operator.attrgetter('name')
Field = partial(attr.ib, default=None)

logging.config.fileConfig(fname='logging.cfg', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
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
        return self.client.get_paged(endpoint, params=params)

    def save_record(self, rec_obj):
        """Update ArchivesSpace record with POST of JSON data."""
        response = self.client.post(rec_obj['uri'], json=rec_obj)
        response.raise_for_status()
        rec_obj.flush()
        logger.info(response.json())
        return response.json()

    def get_aos_for_resource(self, uri):
        """Get archival objects associated with a resource."""
        logger.info(f'Retrieving AOs for {uri}')
        aolist = []
        output = self.client.get(f'{uri}/tree').json()
        for ao_uri in find_key(output, 'record_uri'):
            if 'archival_objects' in ao_uri:
                aolist.append(ao_uri)
        return aolist


class Record(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__persisted = copy.deepcopy(self)

    def flush(self):
        for change in self.changes:
            logger.info(AuditMessage(record=self.__persisted, **change))
        self.__persisted = copy.deepcopy(self)

    @property
    def changes(self):
        return list(jsonpatch.make_patch(self.__persisted, self))

    @property
    def modified(self):
        return bool(self.changes)


class AuditMessage:
    def __init__(self, **kwargs):
        self.record = kwargs['record']
        self.op = kwargs['op']
        self.path = kwargs['path']
        self.kwargs = kwargs

    def __str__(self):
        uri = self.record.get('uri')
        if self.op == 'add':
            new = self.kwargs.get('value')
            msg = {'uri': uri, 'field': self.path, 'old': None, 'new': new}
        elif self.op == 'replace':
            old = jsonpointer.resolve_pointer(self.record, self.path)
            new = self.kwargs.get('value')
            msg = {'uri': uri, 'field': self.path, 'old': old, 'new': new}
        elif self.op == 'remove':
            old = jsonpointer.resolve_pointer(self.record, self.path)
            msg = {'uri': uri, 'field': self.path, 'old': old, 'new': None}
        else:
            msg = {}
        return json.dumps(msg)


# output functions
def download_json(rec_obj):
    """Download a JSON file."""
    uri = rec_obj['uri']
    file_name = uri[1:len(uri)].replace('/', '-')
    f = open(file_name + '.json', 'w')
    json.dump(rec_obj, f)
    f.close()
    return f.name


def create_csv(csv_data, file_name):
    """Create CSV file from list of dicts.

    Example: {'uri': rec_obj.uri,
    'old_value': old_value , 'new_value': new_value}.
    """
    date = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    header = list(csv_data[0].keys())
    full_file_name = os.path.abspath(f'{file_name}{date}.csv')
    with open(full_file_name, 'w') as fp:
        f = csv.DictWriter(fp, fieldnames=header)
        f.writeheader()
        for csv_row in csv_data:
            f.writerow(csv_row)
    return full_file_name


def filter_note_type(rec_obj, note_type):
    """Filter notes by type."""
    return (n for n in rec_obj['notes'] if n.get('type') == note_type)


def replace_str(csv_row, note, old_string='', new_string=''):
    """Replace string and triggers post of updated record if changes are made.
    """
    old_value = note['content']
    new_value = note['content'].replace(old_string, new_string)
    note['content'] = new_value
    if old_value != new_value:
        csv_row['old_values'].append(old_value)
        csv_row['new_values'].append(new_value)
    return csv_row


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
