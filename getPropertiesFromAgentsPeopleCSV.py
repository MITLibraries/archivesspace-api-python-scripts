import json
import requests
import secrets
import csv
import time

secretsVersion = input('To edit production server, enter secrets file name: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}
print('authenticated')

endpoint = '/agents/people?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

records = []
for id in ids:
    endpoint = '/agents/people/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    records.append(output)

f = csv.writer(open('asResults.csv', 'w'))
f.writerow(['uri']+['sort_name']+['authority_id'])
for i in range(0, len(records)):
    uri = records[i]['uri']
    sort_name = records[i]['names'][0]['sort_name']
    authority_id = records[i]['names'][0].get('authority_id', '')
    f.writerow([uri]+[sort_name]+[authority_id])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
