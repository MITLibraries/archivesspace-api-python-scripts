import json
import requests
import secrets
import time
import csv
import argparse
from datetime import datetime

secretsVersion = input('To edit production server, enter secrets filename: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

parser = argparse.ArgumentParser()
parser.add_argument('-1', '--oldValue', help='the value to be replaced.')
parser.add_argument('-2', '--newValue', help='the replacement value.')
args = parser.parse_args()

if args.oldValue:
    oldValue = args.oldValue
else:
    oldValue = input('Enter the value to be replaced: ')
if args.newValue:
    newValue = args.newValue
else:
    newValue = input('Enter the replacement value: ')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL+'/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}
print('authenticated')

endpoint = '/repositories/'+repository+'/digital_objects?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()
print(len(ids))

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

f = csv.writer(open('doUrlEdits_'+dt+'.csv', 'w'))
f.writerow(['endpoint']+['doPost'])

for id in ids:
    print(id)
    endpoint = '/repositories/'+repository+'/digital_objects/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    originalOutput = output
    originalIdValue = output['digital_object_id']
    editedIdValue = originalIdValue.replace(oldValue, newValue)
    output['digital_object_id'] = editedIdValue
    file_versions = output['file_versions']
    fileUriChange = False
    for file_version in file_versions:
        originalUriValue = file_version['file_uri']
        print(originalUriValue)
        editedUriValue = originalUriValue.replace(oldValue, newValue)
        if originalUriValue != editedUriValue:
            file_version['file_uri'] = editedUriValue
            fileUriChange = True
    output['file_versions'] = file_versions
    if (originalIdValue != editedIdValue) or (fileUriChange is True):
        output = json.dumps(output)
        link = baseURL+'/repositories/'+repository+'/digital_objects/'+str(id)
        doPost = requests.post(link, headers=headers, data=output).json()
        print(doPost)
        f.writerow([endpoint]+[doPost])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
