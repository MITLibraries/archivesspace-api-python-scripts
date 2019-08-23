from asnake.client import ASnakeClient
import importlib
import json
import attr
from functools import partial
import operator
import csv
import datetime
import time
import copy

op = operator.attrgetter('name')
Field = partial(attr.ib, default=None)


class Client:
    def __init__(self, secfile):
        """Select secrets.py file for the appropriate instance."""
        secfile_exists = importlib.util.find_spec(secfile)
        if secfile_exists is not None:
            secrets = __import__(secfile)
        else:
            secrets = __import__('secretsDocker')
        print('Editing ' + secfile + ' ' + secrets.baseURL)
        authclient = ASnakeClient(baseurl=secrets.baseURL,
                                  username=secrets.user,
                                  password=secrets.password)
        authclient.authorize()
        self.authclient = authclient

    def get_record(self, uri):
        """Retrieve an individual record."""
        record = self.authclient.get(uri).json()
        print(uri)
        rec_type = record['jsonmodel_type']
        if rec_type == 'resource':
            rec_obj = self._pop_inst(Resource, record)
        elif rec_type == 'accession':
            rec_obj = self._pop_inst(Accession, record)
        elif rec_type == 'archival_object':
            rec_obj = self._pop_inst(ArchivalObject, record)
        else:
            raise Exception("Invalid record type")
        return rec_obj

    def string_search(self, string, repo_id, rec_type):
        """Search for a string across a particular record type."""
        endpoint = (f'repositories/{repo_id}/search?q="{string}'
                    f'"&page_size=100&type[]={rec_type}')
        results = self.authclient.get_paged(endpoint)
        uris = []
        for result in results:
            uri = result['uri']
            uris.append(uri)
        print(len(uris))
        return uris

    def post_record(self, rec_obj, csv_row, csv_data):
        """Update ArchivesSpace record with POST of JSON data."""
        payload = rec_obj.updated_json_string
        payload = json.dumps(payload)
        post = self.authclient.post(rec_obj.uri, data=payload)
        print(post.status_code)
        post = post.json()
        csv_row['post'] = post
        csv_data.append(csv_row)
        print(csv_row)

    def _pop_inst(self, class_type, rec_obj):
        """Populate class instance with data from record."""
        fields = [op(field) for field in attr.fields(class_type)]
        kwargs = {k: v for k, v in rec_obj.items() if k in fields}
        kwargs['json_string'] = rec_obj
        upd_rec = copy.deepcopy(rec_obj)
        kwargs['updated_json_string'] = upd_rec
        rec_obj = class_type(**kwargs)
        return rec_obj


@attr.s
class BaseRecord:
    uri = Field()
    title = Field()
    jsonmodel_type = Field()
    level = Field()
    publish = Field()
    id_0 = Field()
    id_1 = Field()
    id_2 = Field()
    id_3 = Field()
    dates = Field()
    extents = Field()
    instances = Field()
    notes = Field()
    subjects = Field()
    linked_agents = Field()
    label = Field()
    content = Field()
    objtype = Field()
    json_string = Field()
    updated_json_string = Field()
    old_value = Field()
    new_value = Field()


@attr.s
class Resource(BaseRecord):
    related_accessions = Field()
    tree = Field()


@attr.s
class Accession(BaseRecord):
    related_accessions = Field()
    related_resources = Field()


@attr.s
class ArchivalObject(BaseRecord):
    ref_id = Field()
    parent = Field()
    resource = Field()


# output functions
def download_json(rec_obj):
    """Download a JSON file."""
    uri = rec_obj.uri
    file_name = uri[1:len(uri)].replace('/', '-')
    f = open(file_name + '.json', 'w')
    json.dump(rec_obj.json_string, f)
    f.close()


def createcsv(csv_data, file_name):
    """Create CSV file from list of dicts.

    Example: {'uri': rec_obj.uri,
    'old_value': old_value , 'new_value': new_value}.
    """
    date = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    header = list(csv_data[0].keys())
    f = csv.DictWriter(open(file_name + date + '.csv', 'w'), fieldnames=header)
    f.writeheader()
    for csv_row in csv_data:
        f.writerow(csv_row)


def filter_note_type(client, csv_data, rec_obj, note_type, operation,
                     old_string='', new_string=''):
    """Filter notes by type for exporting or editing.

    Triggers post of updated record if changes are made.
    """
    for note in rec_obj.updated_json_string['notes']:
        try:
            if note['type'] == note_type:
                for subnote in note['subnotes']:
                    if operation == 'replace_str':
                        fieldval = subnote['content']
                        new_value = replace_str(rec_obj, fieldval, old_string,
                                                new_string)
                        subnote['content'] = new_value
        except KeyError:
            pass
    return rec_obj


def replace_str(rec_obj, fieldval, old_string, new_string):
    """Replace string in field."""
    old_value = fieldval
    rec_obj.old_value = old_value
    new_value = old_value.replace(old_string, new_string)
    rec_obj.new_value = new_value
    return new_value


def update_record(client, csv_data, rec_obj, log_only=True):
    """Verify record has changed, prepare CSV data, and trigger POST."""
    if rec_obj.updated_json_string != rec_obj.json_string:
        csv_row = {'uri': rec_obj.uri, 'old_value': rec_obj.old_value,
                   'new_value': rec_obj.new_value}
        if log_only is True:
            csv_data.append(csv_row)
            print(csv_row)
        else:
            print('Posting ' + rec_obj.uri)
            client.post_record(rec_obj, csv_row, csv_data)
    else:
        print('Record not posted - ' + rec_obj.uri + ' was not changed')


def find_key(nest_dict, key):
    """Find all instances of a key in a nested dictionary."""
    if key in nest_dict:
        yield nest_dict[key]
    children = nest_dict.get('children')
    if isinstance(children, list):
        for child in children:
            yield from find_key(child, key)


def get_aos_for_resource(client, uri, aolist):
    """Get archival objects associated with a resource."""
    output = client.authclient.get(uri + '/tree').json()
    for ao_uri in find_key(output, 'record_uri'):
        if 'archival_objects' in ao_uri:
            aolist.append(ao_uri)


def elapsed_time(start_time, label):
    """Calculate elapsed time."""
    td = datetime.timedelta(seconds=time.time() - start_time)
    print(label + ': {}'.format(td))


def asmain():
    """Create client and run functions."""
    start_time = time.time()
    client = Client('secretsDocker')

    # res: 1 min, none ao: 3 min, none
    # corrdict = {'IASC': 'DDC'}
    # res: 51 min, 979 ao: 9 min, none
    corr_dict = {'Institute Archives and Special Collections':
                 'Department of Distinctive Collections'}
    # res:  25 min, 193 ao: 192 min, 3
    corr_dict = {'the Institute Archives': 'Distinctive Collections'}
    # res:  14 min, none ao: 192 min, none
    # corrdict = {'Institute Archives': 'Distinctive Collections'}

    error_uris = ['/repositories/2/resources/424',
                  '/repositories/2/resources/1233',
                  '/repositories/2/resources/377',
                  '/repositories/2/resources/356',
                  '/repositories/2/resources/228',
                  '/repositories/2/resources/658',
                  '/repositories/2/resources/635',
                  '/repositories/2/resources/704',
                  '/repositories/2/resources/202',
                  '/repositories/2/resources/586']

    skipped_resources = ['/repositories/2/resources/535',
                         '/repositories/2/resources/41',
                         '/repositories/2/resources/111',
                         '/repositories/2/resources/367',
                         '/repositories/2/resources/231',
                         '/repositories/2/resources/561',
                         '/repositories/2/resources/563',
                         '/repositories/2/resources/103']
    skipped_aos = []
    print('building skipped uris list')
    for uri in skipped_resources:
        get_aos_for_resource(client, uri, skipped_aos)
    skipped_uris = error_uris + skipped_resources + skipped_aos
    print('skipped uris list built')
    csv_data = []
    # rec_type = 'resource'
    rec_type = 'archival_object'
    note_types = ['accessrestrict', 'prefercite']
    for old, new in corr_dict.items():
        uris = client.string_search(old, '2', rec_type)
        remaining = len(uris)
        print(remaining)
        for uri in uris:
            remaining -= 1
            if uri not in skipped_uris:
                for note_type in note_types:
                    print(old, rec_type, note_type, remaining)
                    rec_obj = client.get_record(uri)
                    rec_obj = filter_note_type(client, csv_data, rec_obj,
                                               note_type, 'replace_str', old,
                                               new)
                    update_record(client, csv_data, rec_obj, False)
                    print(len(csv_data))
            else:
                print(uri, ' skipped')
        if len(csv_data) != 0:
            createcsv(csv_data, 'replace_str')
        else:
            print('No files updated')
    elapsed_time(start_time, 'Elapsed time')


if __name__ == '__main__':
    asmain()
