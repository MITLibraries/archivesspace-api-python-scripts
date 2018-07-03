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

endpoint = '/repositories/3/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f=csv.writer(open('resourcesWithBibs.csv', 'wb'))
f.writerow(['uri']+['bibnum'])

for id in ids:
    print id
    uri = '/repositories/3/resources/'+str(id)
    record = requests.get(baseURL + uri, headers=headers).json()
    try:
        bibNum = record['user_defined']['real_1']
        f.writerow([id]+[bibNum])
    except:
        pass

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
