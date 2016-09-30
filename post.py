import json
import requests
import secrets

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

records = json.load(open('[JSON File].json'))
for i in range (0, len (records)):
    record = json.dumps(records[i])
    uri = records[i]['uri']
    post = requests.post(baseURL + uri, headers=headers, data=record).json()
    print post
