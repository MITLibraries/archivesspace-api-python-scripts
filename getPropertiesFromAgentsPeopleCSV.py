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
print 'authenticated'

endpoint = '/agents/people'
arguments = '?page=1&page_size=3000'
output = requests.get(baseURL + endpoint + arguments, headers=headers).json()
records = output['results']

f=csv.writer(open('asResults.csv', 'wb'))
f.writerow(['uri']+['sort_name']+['authority_id'])
for i in range (0, len (records)):
	uri = records[i]['uri']
	sort_name = records[i]['names'][0]['sort_name'].encode('utf-8')
	authority_id = records[i]['names'][0].get('authority_id', '')
	f.writerow([uri]+[sort_name]+[authority_id])
