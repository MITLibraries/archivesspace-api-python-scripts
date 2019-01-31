# This script works to create instances (consisting of top_containers) from a separate CSV file. The CSV file should have two columns, indicator and barcode.
# The directory where this file is stored must match the directory in the filePath variable, below.
# The script will prompt you first for the exact name of the CSV file, and then for the exact resource or accession to attach the containers to.

import json
import requests
import secrets
import csv

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

filePath = '[Enter File Path]'

targetFile = input('Enter file name: ')
targetRecord = input('Enter record type and id (e.g. \'accessions/2049\'): ')

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

csv = csv.DictReader(open(filePath+targetFile))

containerList = []
for row in csv:
    containerRecord = {}
    containerRecord['barcode'] = row['barcode']
    containerRecord['indicator'] = row['indicator']
    containerRecord = json.dumps(containerRecord)
    post = requests.post(baseURL + '/repositories/'+repository+'/top_containers', headers=headers, data=containerRecord).json()
    print(post)
    containerList.append(post['uri'])

asRecord = requests.get(baseURL+'/repositories/'+repository+'/'+targetRecord, headers=headers).json()
instanceArray = asRecord['instances']

for i in range (0, len (containerList)):
    top_container = {}
    top_container['ref'] = containerList[i]
    sub_container = {}
    sub_container['top_container'] = top_container
    instance = {}
    instance['sub_container'] = sub_container
    instance['instance_type'] = 'mixed_materials'
    instanceArray.append(instance)

asRecord['instances'] = instanceArray
asRecord = json.dumps(asRecord)
post = requests.post(baseURL+'/repositories/'+repository+'/'+targetRecord, headers=headers, data=asRecord).json()
print(post)
