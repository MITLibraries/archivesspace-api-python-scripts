import csv
import datetime
from functools import partial
import hashlib
import json
import logging
import logging.config
import operator
import os
import time

import attr


op = operator.attrgetter('name')
Field = partial(attr.ib, default=None)

logging.config.fileConfig(fname='logging.cfg', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class AsOperations:
    def __init__(self, client):
        """Create instance and import client as attribute."""
        self.client = client

    def get_record(self, uri):
        """Retrieve an individual record."""
        record = self.client.get(uri).json()
        return Record(record)

    def search(self, string, repo_id, rec_type):
        """Search for a string across a particular record type."""
        endpoint = (f'repositories/{repo_id}/search?q="{string}'
                    f'"&page_size=100&type[]={rec_type}')
        return self.client.get_paged(endpoint)

    def save_record(self, rec_obj):
        """Update ArchivesSpace record with POST of JSON data."""
        response = self.client.post(rec_obj['uri'], json=rec_obj)
        response.raise_for_status()
        logger.info(response.json())
        return response.json()

    def get_aos_for_resource(self, uri):
        """Get archival objects associated with a resource."""
        aolist = []
        output = self.client.get(f'{uri}/tree').json()
        for ao_uri in find_key(output, 'record_uri'):
            if 'archival_objects' in ao_uri:
                aolist.append(ao_uri)
        return aolist


class Record(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__update_hash()

    def __update_hash(self):
        self.__record_hash = hash_record(self)

    @property
    def modified(self):
        return self.__record_hash != hash_record(self)


def hash_record(record):
    return hashlib.sha1(json.dumps(record, ensure_ascii=False,
                                   sort_keys=True).encode("utf-8")).digest()


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


def filter_note_type(client, csv_data, rec_obj, note_type, operation,
                     old_string='', new_string=''):
    """Filter notes by type for exporting or editing.

    Triggers post of updated record if changes are made.
    """
    for note in [n for n in rec_obj['notes'] if n.get('type') == note_type]:
        for subnote in note.get('subnotes', []):
            csv_row = {'uri': rec_obj['uri'], 'note_type': note_type,
                       'old_value': subnote['content']}
            new_value = subnote['content'].replace(old_string,
                                                   new_string)
            if operation == 'replace_str':
                subnote['content'] = new_value
                if rec_obj.modified is True:
                    csv_row['new_value'] = subnote['content']
                    post = client.save_record(rec_obj['uri'])
                    csv_row['post'] = post
                    csv_data.append(csv_row)
            elif operation == 'find_replace_test':
                if new_string in new_value:
                    csv_row['new_value'] = new_string
                    csv_data.append(csv_row)
    return rec_obj


# def replace_str(field_value, old_string, new_string):
#     """Replace string in field."""
#     old_value = field_value
#     new_value = old_value.replace(old_string, new_string)
#     # if old_value != new_value:
#     #     rec_obj.old_value = old_value
#     #     rec_obj.new_value = new_value
#     return new_value


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
