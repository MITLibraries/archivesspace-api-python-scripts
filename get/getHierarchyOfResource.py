import requests
import secrets
import time
import argparse
import pandas as pd
from datetime import datetime


secretsVersion = input('To edit production server, enter secrets file name: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--id', help='resourceID of the object to retreive.')

args = parser.parse_args()

if args.id:
    resourceID = args.id
else:
    resourceID = input('Enter resource ID: ')

startTime = time.time()


baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL+'/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}


def findKey(d, key):
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j


endpoint = '/repositories/'+repository+'/resources/'+resourceID+'/tree'
print(endpoint)
output = requests.get(baseURL + endpoint, headers=headers).json()
archivalObjects = []
for value in findKey(output, 'record_uri'):
    archivalObjects.append(value)


def addToDict(arcDict, value):
    try:
        rowValue = output[value]
        if rowValue:
            arcDict[value] = rowValue
    except KeyError:
        arcDict[value] = ''


def addToDictNest1(arcDict, value):
    try:
        rowValue = output[value]
        if isinstance(rowValue, dict):
            rowKeys = list(rowValue.keys())
            dictValue = rowValue.get(rowKeys[0])
            arcDict[value] = dictValue
    except KeyError:
        arcDict[value] = ''


arcList = []
for archivalObject in archivalObjects:
    output = requests.get(baseURL + archivalObject, headers=headers).json()
    arcDict = {}
    addToDict(arcDict, 'title')
    addToDict(arcDict, 'uri')
    addToDict(arcDict, 'level')
    addToDict(arcDict, 'jsonmodel_type')
    addToDict(arcDict, 'publish')
    addToDictNest1(arcDict, 'resource')
    addToDictNest1(arcDict, 'parent')
    arcList.append(arcDict)

print('Archival object information collected')


df = pd.DataFrame.from_dict(arcList)
df_titles = df[['title', 'uri', 'parent']].copy()
df = df.rename(columns={'parent': 'level1'})
number = 4
for p in range(1, number):
    parentL1 = 'level'+str(p)
    parentL2 = 'level'+str(p+1)
    df = df.merge(df_titles, how='left', left_on=parentL1, right_on='uri')
    df = df.rename(columns={'uri_x': 'uri', 'title_y': parentL1+'Title',
                   'parent': parentL2})
    del df['uri_y']
    print(df.head(10))

print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv('hierarchyForResource'+resourceID+'_'+dt+'.csv', index=False)


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
