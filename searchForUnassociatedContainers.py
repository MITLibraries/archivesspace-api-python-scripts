import json
import requests
import secrets
import time
import csv

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
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

endpoint = '/search?page=1&page_size=2000&type[]=top_container&filter_term[]={"empty_u_sbool":true}&q="/repositories/3"'

results = requests.get(baseURL + endpoint, headers=headers).json()
results = results['results']

f = csv.writer(open('unassociatedTopContainer.csv', 'w'))
f.writerow(['uri'])

for result in results:
    uri = result['uri']
    f.writerow([uri])

print(len(results))
