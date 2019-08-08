from asnake.client import ASnakeClient
import importlib
import json
import attr


@attr.s
class Client:
    authclient = attr.ib

    def createclient(secfile):
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
        setattr(Client, 'authclient', authclient)

    def getrecord(uri, output):
        """Retrieve an individual record."""
        record = Client.authclient.get(uri).json()
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

        # output
        if output == 'downloadjson':
            downloadjson(recObj)
        else:
            print('Invalid output type')  # likely better ways of handling this
            exit()


@attr.s
class BaseRecord:
    uri = attr.ib
    title = attr.ib
    jsonmodel_type = attr.ib
    level = attr.ib
    publish = attr.ib
    id_0 = attr.ib
    id_1 = attr.ib
    id_2 = attr.ib
    id_3 = attr.ib
    dates = attr.ib
    extents = attr.ib
    instances = attr.ib
    notes = attr.ib
    subjects = attr.ib
    linked_agents = attr.ib
    jsonstring = attr.ib

    def basepop(record):
        """Populate class instance with base data from the record."""
        for key in record:
            try:
                getattr(BaseRecord, key)
                setattr(BaseRecord, key, record[key])
            except AttributeError:
                pass
            except KeyError:
                pass
        BaseRecord.jsonstring = record

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
class Resource (BaseRecord):
    related_accessions = attr.ib
    tree = attr.ib
    keylist = ['related_accessions', 'tree']


@attr.s
class Accession (BaseRecord):
    related_accessions = attr.ib
    related_resources = attr.ib
    keylist = ['related_accessions', 'related_resources']


@attr.s
class ArchivalObject (BaseRecord):
    ref_id = attr.ib
    parent = attr.ib
    resource = attr.ib
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
    Client.createclient('secretsDev')
    Client.getrecord('/repositories/2/resources/562', 'downloadjson')
    Client.getrecord('/repositories/2/accessions/16', 'downloadjson')
    Client.getrecord('/repositories/2/archival_objects/275186', 'downloadjson')
    Client.getrecord('/repositories/2/archival_objects/297132', 'downloadjson')


if __name__ == '__main__':
    asmain()
