import json
import requests
import secrets
import time

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

startTime = time.time()

def findKey(d, key):
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

resourceID= input('Enter resource ID: ')

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/'+repository+'/resources/'+resourceID+'/tree'

output = requests.get(baseURL + endpoint, headers=headers).json()
archivalObjects = []
for value in findKey(output, 'record_uri'):
    print(value)
    if 'archival_objects' in value:
        archivalObjects.append(value)

print('downloading aos')
records = []
for archivalObject in archivalObjects:
    output = requests.get(baseURL + archivalObject, headers=headers).json()
    records.append(output)

print('creating file')
f=open('archivalObjects.json', 'w')
json.dump(records, f)
f.close()
print('file done')
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
