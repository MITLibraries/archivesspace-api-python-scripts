from asnake.client import ASnakeClient
import importlib
import json
import attr
from functools import partial
import operator

f = operator.attrgetter('name')
Field = partial(attr.ib, default=None)

class Client:

    def __init__(self, secfile):
        """Select secrets.py file for the appropriate instance."""
        secfileExists = importlib.util.find_spec(secfile)
        print(secfileExists)
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

        # record type
        if recType == 'resource':
            fields = [f(field) for field in attr.fields(Resource)]
            kwargs = {k: v for k, v in record.items() if k in fields}
            kwargs['jsonstr'] = record
            kwargs['updjsonstr'] = record
            rec = Resource(**kwargs)
        elif recType == 'accession':
            fields = [f(field) for field in attr.fields(Accession)]
            kwargs = {k: v for k, v in record.items() if k in fields}
            kwargs['jsonstr'] = record
            kwargs['updjsonstr'] = record
            rec = Resource(**kwargs)
        elif recType == 'archival_object':
            fields = [f(field) for field in attr.fields(ArchivalObject)]
            kwargs = {k: v for k, v in record.items() if k in fields}
            kwargs['jsonstr'] = record
            kwargs['updjsonstr'] = record
            rec = Resource(**kwargs)
        else:
            print('Invalid record type')  # likely better ways of handling this
            exit()
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


def asmain():
    """Create client and run functions."""
    client = Client('secretsDocker')
    rec = client.getrecord('/repositories/2/resources/562')


if __name__ == '__main__':
    asmain()
