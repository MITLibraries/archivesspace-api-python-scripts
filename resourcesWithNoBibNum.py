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
session = auth['session']
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/'+repository+'/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f=csv.writer(open('resourcesWithNoBibs.csv', 'w'))
f.writerow(['uri'])

for id in ids:
    print(id)
    uri = '/repositories/'+repository+'/resources/'+str(id)
    record = requests.get(baseURL + uri, headers=headers).json()
    try:
        print(record['user_defined']['real_1'])
    except:
        f.writerow([uri])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
