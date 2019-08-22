from asnake.client import ASnakeClient
import importlib
import json
import attr
from functools import partial
import operator
import csv
import datetime
import copy

op = operator.attrgetter('name')
Field = partial(attr.ib, default=None)


class Client:
    def __init__(self, secfile):
        """Select secrets.py file for the appropriate instance."""
        secfileExists = importlib.util.find_spec(secfile)
        if secfileExists is not None:
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
        recType = record['jsonmodel_type']
        if recType == 'resource':
            rec = self._pop_inst(Resource, record)
        elif recType == 'accession':
            rec = self._pop_inst(Accession, record)
        elif recType == 'archival_object':
            rec = self._pop_inst(ArchivalObject, record)
        else:
            raise Exception("Invalid record type")
        return rec

    def string_search(self, string, repoid, rectype):
        """Search for a string across a particular record type."""
        endpoint = (f'repositories/{repoid}/search?q="{string}'
                    f'"&page_size=100&type[]={rectype}')
        results = self.authclient.get_paged(endpoint)
        uris = []
        for result in results:
            uri = result['uri']
            uris.append(uri)
        print(len(uris))
        return uris

    def post_record(self, rec, csvrow, csvdata):
        """Update ArchivesSpace record with POST of JSON data."""
        payload = rec.updjsonstr
        payload = json.dumps(payload)
        post = self.authclient.post(rec.uri, data=payload)
        print(post.status_code)
        post = post.json()
        csvrow['post'] = post
        csvdata.append(csvrow)
        print(csvrow)

    def _pop_inst(self, classtype, rec):
        """Populate class instance with data from record."""
        fields = [op(field) for field in attr.fields(classtype)]
        kwargs = {k: v for k, v in rec.items() if k in fields}
        kwargs['jsonstr'] = rec
        updrec = copy.deepcopy(rec)
        kwargs['updjsonstr'] = updrec
        rec = classtype(**kwargs)
        return rec


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
    jsonstr = Field()
    updjsonstr = Field()
    oldval = Field()
    newval = Field()


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
def download_json(rec):
    """Download a JSON file."""
    uri = rec.uri
    filename = uri[1:len(uri)].replace('/', '-')
    f = open(filename + '.json', 'w')
    json.dump(rec.jsonstr, f)
    f.close()


def createcsv(csvdata, filename):
    """Create CSV file from list of dicts.

    Example: {'uri': rec.uri,
    'oldvalue': oldsub, 'newvalue': newvalue}.
    """
    date = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    header = list(csvdata[0].keys())
    f = csv.DictWriter(open(filename + date + '.csv', 'w'), fieldnames=header)
    f.writeheader()
    for csvrow in csvdata:
        f.writerow(csvrow)


def filternotetype(client, csvdata, rec, notetype, operation, oldstr='',
                   newstr=''):
    """Filter notes by type for exporting or editing.

    Triggers post of updated record if changes are made.
    """
    for note in rec.updjsonstr['notes']:
        try:
            if note['type'] == notetype:
                for subnote in note['subnotes']:
                    if operation == 'replacestr':
                        fieldval = subnote['content']
                        newval = replacestr(rec, fieldval, oldstr, newstr)
                        subnote['content'] = newval
        except KeyError:
            pass
    return rec


def replacestr(rec, fieldval, oldstr, newstr):
    """Replace string in field."""
    oldval = fieldval
    rec.oldval = oldval
    newval = oldval.replace(oldstr, newstr)
    rec.newval = newval
    return newval


def update_record(client, csvdata, rec):
    """Verify record has changed, prepare CSV data, and trigger POST."""
    if rec.updjsonstr != rec.jsonstr:
        csvrow = {'uri': rec.uri, 'oldvalue': rec.oldval, 'newvalue':
                  rec.newval}
        client.post_record(rec, csvrow, csvdata)
    else:
        print('Record not posted - ' + rec.uri + ' was not changed')


def find_key(nestDict, key):
    """Find all instances of a key in a nested dictionary."""
    if key in nestDict:
        yield nestDict[key]
    children = nestDict.get("children")
    if isinstance(children, list):
        for child in children:
            yield from find_key(child, key)


def get_aos_for_resource(client, uri, aolist):
    """Get archival objects associated with a resource."""
    output = client.authclient.get(uri + '/tree').json()
    for aoUri in find_key(output, 'record_uri'):
        if 'archival_objects' in aoUri:
            aolist.append(aoUri)


def asmain():
    """Create client and run functions."""
    client = Client('secretsDocker')

    erroruris = ['/repositories/2/resources/424',
                 '/repositories/2/resources/1233',
                 '/repositories/2/resources/377',
                 '/repositories/2/resources/356',
                 '/repositories/2/resources/228',
                 '/repositories/2/resources/658',
                 '/repositories/2/resources/635',
                 '/repositories/2/resources/704',
                 '/repositories/2/resources/202',
                 '/repositories/2/resources/586']

    skippedresources = ['/repositories/2/resources/535',
                        '/repositories/2/resources/41',
                        '/repositories/2/resources/111',
                        '/repositories/2/resources/367',
                        '/repositories/2/resources/231',
                        '/repositories/2/resources/561',
                        '/repositories/2/resources/563',
                        '/repositories/2/resources/103']
    skippedaos = []
    print('building skipped uris list')
    for uri in skippedresources:
        get_aos_for_resource(client, uri, skippedaos)
    skippeduris = erroruris + skippedresources + skippedaos
    print('skipped uris list built')
    csvdata = []
    rectype = 'resource'
    # rectype = 'archival_object'
    notetypes = ['accessrestrict', 'prefercite']
    for old, new in corrdict.items():
        uris = client.string_search(old, '2', rectype)
        remaining = len(uris)
        print(remaining)
        for uri in uris:
            remaining -= 1
            if uri not in skippeduris:
                for notetype in notetypes:
                    print(old, rectype, notetype, remaining)
                    rec = client.get_record(uri)
                    rec = filternotetype(client, csvdata, rec, notetype,
                                         'replacestr', old, new)
                    update_record(client, csvdata, rec)
            else:
                print(uri, ' skipped')
        if len(csvdata) != 0:
            createcsv(csvdata, 'replacestr')
        else:
            print('No files updated')
    label = 'Elapsed time'
    td = datetime.timedelta(seconds=time.time() - startTime)
    print(label + ': {}'.format(td))


if __name__ == '__main__':
    asmain()
