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

endpoint = '/agents/corporate_entities'
arguments = '?page=1&page_size=3000'
output = requests.get(baseURL + endpoint + arguments, headers=headers).json()
f=csv.writer(open('asAgentsCorporate.csv', 'wb'))
f.writerow(['uri']+['sort_name']+['authority_id']+['names'])
for i in range (0, len (output['results'])):
	f.writerow([json.dumps(output['results'][i]['uri']).replace('"','')]+[json.dumps(output['results'][i]['names'][0]['sort_name'], ensure_ascii=False).encode('utf-8').replace('"','')]+[json.dumps(output['results'][i]['names'][0].get('authority_id', 'undefined')).replace('"','')]+[json.dumps(output['results'][i]['names'], ensure_ascii=False).encode('utf8')])
