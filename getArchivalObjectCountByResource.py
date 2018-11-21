import json
import requests
import secrets
import time
import csv

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Development'
else:
    print 'Editing Development'

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

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/3/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()
print len(ids)

f=csv.writer(open('archivalObjectCountByResource.csv', 'wb'))
f.writerow(['title']+['bib']+['uri']+['id_0']+['id_1']+['id_2']+['id_3']+['aoCount'])

records = []
for id in ids:
    print id
    endpoint = '/repositories/3/resources/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    title = output['title'].encode('utf-8')
    uri = output['uri']
    id0 = output['id_0']
    try:
        bib = output['user_defined']['real_1']
    except:
        bib = ''
    try:
        id1 = output['id_1']
    except:
        id1=''
    try:
        id2 = output['id_2']
    except:
        id2 = ''
    try:
        id3 = output['id_3']
    except:
        id3=''

    treeEndpoint = '/repositories/3/resources/'+str(id)+'/tree'

    output2 = requests.get(baseURL + treeEndpoint, headers=headers).json()
    archivalObjects = []
    for value in findKey(output2, 'record_uri'):
        print value
        if 'archival_objects' in value:
            archivalObjects.append(value)
    aoCount = len(archivalObjects)
    f.writerow([title]+[bib]+[uri]+[id0]+[id1]+[id2]+[id3]+[aoCount])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
