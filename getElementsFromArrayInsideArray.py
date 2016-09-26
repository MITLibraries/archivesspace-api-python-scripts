import json
import requests
import csv

baseURL = '[ArchivesSpace URL]'
user='[username]'
password='[password]'

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/agents/people'
arguments = '?page=1&page_size=3000'
output = requests.get(baseURL + endpoint + arguments, headers=headers).json()
f=csv.writer(open('asArrayResults.csv', 'wb'))
f.writerow(['uri']+['begin']+['end']+['expression'])
for i in range (0, len (output['results'])):
	for j in range (0, len (output['results'][i]['dates_of_existence'])):
		f.writerow([json.dumps(output['results'][i]['uri']).replace('"','')]+[json.dumps(output['results'][i]['dates_of_existence'][j].get('begin','none')).replace('"','')]+[json.dumps(output['results'][i]['dates_of_existence'][j].get('end','none')).replace('"','')]+[json.dumps(output['results'][i]['dates_of_existence'][j].get('expression','none')).replace('"','')])
