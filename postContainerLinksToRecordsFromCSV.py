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

targetFile = input('Enter file name: ')

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

csvfile = csv.DictReader(open(targetFile))

f=csv.writer(open('containerLinksPostedFromCSV.csv', 'w'))
f.writerow(['topContainer']+['resource']+['post'])

for row in csvfile:
    uri = row['uri']
    resourceUri = row['resourceuri']
    print(baseURL+resourceUri)
    asRecord = requests.get(baseURL+resourceUri, headers=headers).json()
    instanceArray = asRecord['instances']
    top_container = {}
    top_container['ref'] = uri
    sub_container = {}
    sub_container['top_container'] = top_container
    instance = {}
    instance['sub_container'] = sub_container
    instance['instance_type'] = 'mixed_materials'
    instanceArray.append(instance)
    asRecord['instances'] = instanceArray
    asRecord = json.dumps(asRecord)
    post = requests.post(baseURL+resourceUri, headers=headers, data=asRecord).json()
    print(post)
    f.writerow([uri]+[resourceUri]+[post])
