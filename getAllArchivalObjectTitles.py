import json
import requests
import secrets
import time
import csv

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print 'authenticated'

endpoint = '/repositories/3/archival_objects?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()
print len(ids)

f=csv.writer(open('archivalObjectTitles.csv', 'wb'))
f.writerow(['title']+['uri'])

for id in ids:
    print id
    endpoint = '/repositories/3/archival_objects/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    try:
        title = output['title'].encode('utf-8')
    except:
        title = ''
    uri = output['uri']
    print title, uri
    f.writerow([title]+[uri])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
