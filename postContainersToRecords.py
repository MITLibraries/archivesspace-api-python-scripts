import json
import requests
import secrets
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

targetFile = raw_input('Enter file name: ')
targetRecord = raw_input('Enter record type and id (e.g. \'accessions/2049\'): ')

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

csv = csv.DictReader(open(targetFile))

asRecord = requests.get(baseURL+'/repositories/'+repository+'/'+targetRecord, headers=headers).json()
print baseURL+'/repositories/'+repository+'/'+targetRecord
f=open(targetRecord+'asRecordBackup.json', 'w')
json.dump(asRecord, f)
instanceArray = asRecord['instances']

for row in csv:
    uri = row['uri']
    print uri
    top_container = {}
    top_container['ref'] = uri
    sub_container = {}
    sub_container['top_container'] = top_container
    instance = {}
    instance['sub_container'] = sub_container
    instance['instance_type'] = 'mixed_materials'
    instanceArray.append(instance)
asRecord['instances'] = instanceArray
f2=open(targetRecord+'asRecordModified.json', 'w')
json.dump(asRecord, f2)
asRecord = json.dumps(asRecord)
post = requests.post(baseURL+'/repositories/'+repository+'/'+targetRecord, headers=headers, data=asRecord).json()
print post
