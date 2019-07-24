from asnake.client import ASnakeClient
import importlib
import json

# generic attributes used across several classes
genattrlist = ['uri', 'title', 'jsonmodel_type', 'level', 'publish', 'id_0',
               'id_1', 'id_2', 'id_3', 'dates', 'extents', 'instances',
               'notes', 'subjects', 'linked_agents']
classDict = {'resource': 'Resource', 'accession': 'Accession',
             'archival_object': 'ArchivalObject'}


class Resource:

    def __init__(self, record):
        """Create a class for an ArchivesSpace resource record."""
        keyList = ['related_accessions', 'tree'] + genattrlist
        constructor(self, record, keyList)


class Accession:

    def __init__(self, record):
        """Create a class for an ArchivesSpace accession record."""
        keyList = ['related_resources'] + genattrlist
        constructor(self, record, keyList)


class ArchivalObject:

    def __init__(self, record):
        """Create a class for an ArchivesSpace archival object record."""
        keyList = ['refid', 'parent', 'resource'] + genattrlist
        constructor(self, record, keyList)


# client function
def createclient(secfile):
    """Select secrets.py file for the appropriate ArchivesSpace instance."""
    secfileExists = importlib.util.find_spec(secfile)
    if secfileExists is not None:
        secrets = __import__(secfile)
    else:
        secrets = __import__('secrets')
    print('Editing ' + secfile + ' ' + secrets.baseURL)
    client = ASnakeClient(baseurl=secrets.baseURL,
                          username=secrets.user,
                          password=secrets.password)
    client.authorize()
    return client


# operation functions
def getrecord(uri, client, output):
    """Retrieve an individual record."""
    record = client.get(uri).json()
    recType = record['jsonmodel_type']
    classType = eval(classDict[recType])
    recObj = classType(record)
    print(recObj.jsonmodel_type)
    output = eval(output)
    output(recObj)


# component functions
def constructor(self, record, keyList):
    """Construct class attributes."""
    for key in record:
        if key in keyList:
            setattr(self, key, record[key])
        self.json = record


# output functions
def downloadjson(recObj):
    """Download a JSON file."""
    uri = recObj.uri
    filename = uri[1:len(uri)].replace('/', '-')
    f = open(filename + '.json', 'w')
    json.dump(recObj.json, f)
    f.close()


def asmain():
    """Create client and run functions."""
    client = createclient('secretsDev')
    getrecord('/repositories/2/resources/562', client, 'downloadjson')


if __name__ == '__main__':
    asmain()
