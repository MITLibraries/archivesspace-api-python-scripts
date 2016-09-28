import json
import requests
import secrets

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

agents = json.load(open('agents.json'))
for i in range (0, len (agents)):
    agent = json.dumps(agents[i])
    post = requests.post(baseURL + '/agents/people', headers=headers, data=agent).json()
    print post
