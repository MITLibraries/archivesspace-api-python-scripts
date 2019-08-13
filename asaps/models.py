from asnake.client import ASnakeClient
import importlib
import json
import attr


class Client:

    def __init__(self, secfile):
        """Select secrets.py file for the appropriate instance."""
        secfileExists = importlib.util.find_spec(secfile)
        if secfileExists is not None:
            secrets = __import__(secfile)
        else:
            secrets = __import__('secrets')
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
            recObj = Resource.classpop(record, Resource)
        elif recType == 'accession':
            recObj = Accession.classpop(record, Accession)
        elif recType == 'archival_object':
            recObj = ArchivalObject.classpop(record, ArchivalObject)
        else:
            print('Invalid record type')  # likely better ways of handling this
            exit()
        return recObj


@attr.s
class BaseRecord:
    uri = attr.ib()
    title = attr.ib()
    jsonmodel_type = attr.ib()
    level = attr.ib()
    publish = attr.ib()
    id_0 = attr.ib()
    id_1 = attr.ib()
    id_2 = attr.ib()
    id_3 = attr.ib()
    dates = attr.ib()
    extents = attr.ib()
    instances = attr.ib()
    notes = attr.ib()
    subjects = attr.ib()
    linked_agents = attr.ib()
    label = attr.ib()
    content = attr.ib()
    objtype = attr.ib()
    jsonstr = attr.ib()
    updjsonstr = attr.ib()

    def basepop(record):
        """Populate class instance with base data from the record."""
        for key in record:
            if key == 'type':
                setattr(BaseRecord, 'objtype', record[key])
            else:
                try:
                    setattr(BaseRecord, key, record[key])
                except AttributeError:
                    pass
                except KeyError:
                    pass
        BaseRecord.jsonstr = record
        BaseRecord.updjsonstr = record

    def classpop(record, objclass):
        """Populate class instance with class specific data from the record."""
        BaseRecord.basepop(record)
        for key in objclass.keylist:
            try:
                record[key]
                setattr(objclass, key, record[key])
            except KeyError:
                pass
        return objclass


@attr.s
class Resource(BaseRecord):
    related_accessions = attr.ib()
    tree = attr.ib()
    keylist = ['related_accessions', 'tree']


@attr.s
class Accession(BaseRecord):
    related_accessions = attr.ib()
    related_resources = attr.ib()
    keylist = ['related_accessions', 'related_resources']


@attr.s
class ArchivalObject(BaseRecord):
    ref_id = attr.ib()
    parent = attr.ib()
    resource = attr.ib()
    keylist = ['ref_id', 'parent', 'resource']


# output functions
def downloadjson(recObj):
    """Download a JSON file."""
    uri = recObj.uri
    filename = uri[1:len(uri)].replace('/', '-')
    f = open(filename + '.json', 'w')
    json.dump(recObj.jsonstring, f)
    f.close()


def asmain():
    """Create client and run functions."""
    client = Client('secretsDev')
    recObj = client.getrecord('/repositories/2/resources/562')


if __name__ == '__main__':
    asmain()
