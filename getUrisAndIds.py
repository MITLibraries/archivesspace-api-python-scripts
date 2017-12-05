import json
import requests
import secrets
import csv

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

recordType = raw_input('Enter record type, either \'resources\' or \'accessions\': ')

endpoint = '/repositories/3/'+recordType+'?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f=csv.writer(open(recordType+'UrisAndIds.csv', 'wb'))
f.writerow(['ConCatID']+['id_0']+['id_1']+['id_2']+['id_3']+['id'])

for id in ids:
    print id
    output = requests.get(baseURL + endpoint, headers=headers).json()
    try:
    except:
    try:
        id_1 = '.'+output['id_1']
    except:
    try:
        id_2 = '.'+output['id_2']
    except:
        id_2 = ''
    try:
        id_3 = '.'+output['id_3']
    except:
    ConCatID = id_0+id_1+id_2+id_3
