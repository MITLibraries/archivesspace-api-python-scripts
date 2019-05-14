import json
import requests
import secrets
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--entity', help='enter either "people", "corporate_entites", or "families". optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.entity:
    type_entity = args.entity
    print(type_entity)
else:
    type_entity = input('Enter type of entity-- either "people", "corporate_entities", or "families": ')

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
print(baseURL + '/users/'+user)
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
print(auth)
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print('authenticated')

endpoint = '/agents/'+type_entity+'?all_ids=true'
print(endpoint)

ids = requests.get(baseURL + endpoint, headers=headers).json()

f=csv.writer(open('notPublished'+type_entity+'.csv', 'w'))
f.writerow(['uri']+['publish']+['name']+['date']+['rules']+['creator'])

total = len(ids)
for id in ids:
    print('id', id, total, 'records remaining')
    total = total - 1
    endpoint = '/agents/'+type_entity+'/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()

    uri = output['uri']
    name = output['names'][0]['sort_name'].strip()
    create_time = output['create_time']
    try:
        created_by = output['created_by']
    except:
        created_by = ''
    try:
        rules = output['names'][0]['rules']
    except:
        rules = ''
    try:
        publish = output['publish']
        if not publish:
            f.writerow([uri]+[publish]+[name]+[create_time]+[rules]+[created_by])
    except:
        publish = ''
        f.writerow([uri]+[publish]+[name]+[create_time]+[rules]+[created_by])
    else:
        pass
