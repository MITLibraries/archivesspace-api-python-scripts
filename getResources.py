import json
import requests
import secrets

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/3/resources?page=1&page_size=3000'

output = requests.get(baseURL + endpoint, headers=headers).json()
f=open('resources.json', 'w')
results=(json.dump(output['results'], f))
f.close()
