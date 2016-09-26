import json
import requests

baseURL = '[ArchivesSpace URL]'
user='[username]'
password='[password]'

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/3/resources/830'

output = requests.get(baseURL + endpoint, headers=headers).json()
f=open('ASrecord.json', 'w')
results=(json.dump(output, f))
f.close()
