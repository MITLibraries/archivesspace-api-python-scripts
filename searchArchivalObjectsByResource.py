import json
import requests
import secrets

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

resourceNumber = '1051'#Update 'resourceNumber' with the resource number for which you wish to find all of the archival objects

resource ='\"/repositories/3/resources/'+resourceNumber+'\"'
payload = {'page': '1', 'page_size': '3000', 'q': resource }

search = requests.get(baseURL+'/search', headers=headers, params=payload).json()
arrayURI = []
for i in range (0, len (search['results'])):
    if search['results'][i]['jsonmodel_type'] == 'archival_object':
        uri = search['results'][i]['uri']
        arrayURI.append(uri)

f=open('asSearchResults.json', 'w')
arrayJSON = []
for j in arrayURI:
    output = requests.get(baseURL+j, headers=headers).json()
    arrayJSON.append(output)

json.dump(arrayJSON, f)
