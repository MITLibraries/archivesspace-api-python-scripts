import json
import requests
import secrets
import time

startTime = time.time()

def findKey(d, key):
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list):
            for i in d[k]:
                for j in findKey(i, key):
                    yield j

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

resourceID= raw_input('Enter resource ID: ')

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/3/resources/'+resourceID+'/tree'

output = requests.get(baseURL + endpoint, headers=headers).json()

archivalObjects = []
for value in findKey(output, 'record_uri'):
    if 'archival_objects' in value:
        archivalObjects.append(value)

records = []
for archivalObject in archivalObjects:
    output = requests.get(baseURL + archivalObject, headers=headers).json()
    records.append(output)

f=open('archivalObjects.json', 'w')
json.dump(records, f)
f.close()

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
