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

    def getrec(self, uri):
        """Retrieve an individual record."""
        rec = self.authclient.get(uri).json()
        print(uri)
        recType = rec['jsonmodel_type']
        if recType == 'resource':
            rec = self.popinst(Resource, rec)
        elif recType == 'accession':
            rec = self.popinst(Accession, rec)
        elif recType == 'archival_object':
            rec = self.popinst(ArchivalObject, rec)
        else:
            print('Invalid record type')
            exit()
        return rec

    def stringsearch(self, string, repoid, rectype):
        """Search for a string across a particular record type."""
        endpoint = ('repositories/' + str(repoid) + '/search?q="'
                    + string + '"&page_size=100&type[]=' + rectype)
        results = self.authclient.get_paged(endpoint)
        uris = []
        for result in results:
            uri = result['uri']
            uris.append(uri)
        print(len(uris))
        return uris

    def postrec(self, rec, csvrow, csvdata):
        """Update ArchivesSpace record with POST of JSON data."""
        payload = rec.updjsonstr
        payload = json.dumps(payload)
        post = self.authclient.post(rec.uri, data=payload)
        print(post.status_code)
        post = post.json()
        csvrow['post'] = post
        csvdata.append(csvrow)
        print(csvrow)

    def popinst(self, classtype, rec):
        """Populate class instance with data from record."""
        fields = [op(field) for field in attr.fields(classtype)]
        kwargs = {k: v for k, v in rec.items() if k in fields}
        kwargs['jsonstr'] = rec
        updrec = copy.copy(rec)
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
def downloadjson(rec):
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


def filternotetype(client, csvdata, rec, notetype, operation, old='', new=''):
    """Filter notes by type for exporting or editing.

    Triggers post of updated record if changes are made.
    """
    update = False
    for note in rec.updjsonstr['notes']:
        if 'type' in note:
            if note['type'] == notetype:
                if 'subnotes' in note:
                    for subnote in note['subnotes']:
                        if operation == 'replacestr':
                            oldsub = subnote['content']
                            updsub = subnote['content']
                            subnote['content'] = updsub.replace(old, new)
                            if oldsub != subnote['content']:
                                update = True
    if update is True:
        csvrow = {'uri': rec.uri, 'oldvalue': oldsub, 'newvalue':
                  subnote['content']}
        client.postrec(rec, csvrow, csvdata)
    else:
        print('Record not posted - ' + rec.uri + ' was not changed')


def asmain():
    """Create client and run functions."""
    client = Client('secretsDocker')
    corrdict = {'Institute Archives': 'Distinctive Collections'}
    csvdata = []
    skippeduris = ['/repositories/2/resources/424',
                   '/repositories/2/resources/1233',
                   '/repositories/2/resources/377',
                   '/repositories/2/resources/356',
                   '/repositories/2/resources/228',
                   '/repositories/2/resources/658',
                   '/repositories/2/resources/635',
                   '/repositories/2/resources/704',
                   '/repositories/2/resources/202',
                   '/repositories/2/resources/586'
                   ]
    rectype = 'resource'
    for old, new in corrdict.items():
        uris = client.stringsearch(old, '2', rectype)
        remaining = len(uris)
        for uri in uris:
            remaining -= 1
            if uri not in skippeduris:
                print(remaining)
                rec = client.getrecord(uri)
                filternotetype(client, csvdata, rec, 'accessrestrict',
                               'replacestr', old, new)
                filternotetype(client, csvdata, rec, 'prefercite',
                               'replacestr', old, new)
    createcsv(csvdata, 'replacestr')


if __name__ == '__main__':
    asmain()
