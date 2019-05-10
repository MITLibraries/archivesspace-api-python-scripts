import json
import requests
import secrets
import time
import csv
import argparse
from datetime import datetime

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

parser = argparse.ArgumentParser()
parser.add_argument('-1', '--replacedValue', help='the value to be replaced. optional - if not provided, the script will ask for input')
parser.add_argument('-2', '--replacementValue', help='the replacement value. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.replacedValue:
    replacedValue = args.replacedValue
else:
    replacedValue = input('Enter the value to be replaced: ')
if args.replacementValue:
    replacementValue = args.replacementValue
else:
    replacementValue = input('Enter the replacement value: ')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print('authenticated')

endpoint = '/repositories/'+repository+'/digital_objects?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()
print(len(ids))

f=csv.writer(open('doUrlEdits'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f.writerow(['endpoint']+['doPost'])

for id in ids:
    print(id)
    endpoint = '/repositories/'+repository+'/digital_objects/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    originalOutput = output
    originalIdValue = output['digital_object_id']
    editedIdValue = originalIdValue.replace(replacedValue, replacementValue)
    output['digital_object_id'] = editedIdValue
    file_versions = output['file_versions']
    fileUriChange = False
    for file_version in file_versions:
        originalUriValue = file_version['file_uri']
        print(originalUriValue)
        editedUriValue = originalUriValue.replace(replacedValue, replacementValue)
        if originalUriValue != editedUriValue:
            file_version['file_uri'] = editedUriValue
            fileUriChange = True
    output['file_versions'] = file_versions
    if originalIdValue != editedIdValue or fileUriChange == True:
        output = json.dumps(output)
        doPost = requests.post(baseURL + '/repositories/'+repository+'/digital_objects/'+str(id), headers=headers, data=output).json()
        print(doPost)
        f.writerow([endpoint]+[doPost])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
