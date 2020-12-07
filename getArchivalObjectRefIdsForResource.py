import requests
import secrets
import time
import pandas as pd
from datetime import datetime

secretsVersion = input('To edit production server, enter secrets file: ')
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

auth = requests.post(baseURL+'/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}

resourceID = input('Enter resource ID: ')

endpoint = '/repositories/'+repository+'/resources/'+resourceID+'/tree'

output = requests.get(baseURL + endpoint, headers=headers).json()
print(output)
archivalObjects = []
for value in findKey(output, 'record_uri'):
    print(value)
    if 'archival_objects' in value:
        archivalObjects.append(value)

print('downloading aos')

fieldList = ['title', 'uri', 'ref_id', 'level']
objectList = []
for archivalObject in archivalObjects:
    output = requests.get(baseURL + archivalObject, headers=headers).json()
    aoDict = {}
    for x in fieldList:
        value = output.get(x)
        aoDict[x] = value
    if output.get('dates'):
        express = output['dates'][0].get('expression')
        begin = output['dates'][0].get('begin')
        aoDict['dateExpression'] = express
        aoDict['dateBegin'] = begin
    if output.get('instances'):
        sub_container = output['instances'][0].get('sub_container')
        top_container = sub_container.get('top_container')
        aoDict['container_type'] = sub_container.get('type_2')
        aoDict['container_num'] = sub_container.get('indicator_2')
        aoDict['top_container'] = top_container.get('ref')
    objectList.append(aoDict)


df = pd.DataFrame.from_dict(objectList)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='RefIds'+resourceID+'_'+dt+'.csv', index=False)


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
