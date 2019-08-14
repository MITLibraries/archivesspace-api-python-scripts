from asnake.client import ASnakeClient
import importlib
import json
import attr
from functools import partial
import operator
import csv
import datetime

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

    def getrecord(self, uri):
        """Retrieve an individual record."""
        record = self.authclient.get(uri).json()
        print(uri)
        recType = record['jsonmodel_type']
        if recType == 'resource':
            fields = [op(field) for field in attr.fields(Resource)]
            kwargs = {k: v for k, v in record.items() if k in fields}
            kwargs['jsonstr'] = record
            kwargs['updjsonstr'] = record
            rec = Resource(**kwargs)
        elif recType == 'accession':
            fields = [op(field) for field in attr.fields(Accession)]
            kwargs = {k: v for k, v in record.items() if k in fields}
            kwargs['jsonstr'] = record
            kwargs['updjsonstr'] = record
            rec = Accession(**kwargs)
        elif recType == 'archival_object':
            fields = [op(field) for field in attr.fields(ArchivalObject)]
            kwargs = {k: v for k, v in record.items() if k in fields}
            kwargs['jsonstr'] = record
            kwargs['updjsonstr'] = record
            rec = ArchivalObject(**kwargs)
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

    def postrecord(self, rec, csvrow, csvdata):
        """Update ArchivesSpace record with POST of JSON data."""
        payload = rec.updjsonstr
        payload = json.dumps(payload)
        post = self.authclient.post(rec.uri, data=payload)
        print(post.status_code)
        post = post.json()
        csvrow['post'] = post
        csvdata.append(csvrow)
        print(csvrow)


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
def asmain():
    """Create client and run functions."""
    csvdata = []
    client = Client('secretsDocker')
    rec = client.getrecord('/repositories/2/resources/562')


if __name__ == '__main__':
    asmain()
