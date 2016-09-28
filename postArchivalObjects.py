import json
import requests
import secrets

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

archivalObjects = json.load(open('archival_objects.json'))
for i in range (0, len (archivalObjects)):
    archivalObject = json.dumps(archivalObjects[i])
    uri = archivalObjects[i]['uri']
    post = requests.post(baseURL + uri, headers=headers, data=archivalObject).json()
    print post
