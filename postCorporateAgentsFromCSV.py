import json
import requests
import csv
import secrets
import time

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

targetFile = raw_input('Enter file name: ')

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

f=csv.writer(open('postNewCorporateAgents.csv', 'wb'))
f.writerow(['sortName']+['uri'])

csvfile = csv.DictReader(open(targetFile))

for row in csvfile:
    agentRecord = {}
    names = []
    name = {}
    name['primary_name'] = row['primary']
    name['sort_name'] = row['sortName']
    name['jsonmodel_type'] = 'name_corporate_entity'
    name['name_order'] = 'direct'
    name['rules'] = 'rda'
    try:
        name['subordinate_name_1'] = row['subordinate_1']
    except:
        pass
    try:
        name['subordinate_name_2'] = row['subordinate_2']
    except:
        pass
    try:
        name['authority_id'] = row['authorityID']
        name['source'] = 'viaf'
    except:
        pass
    names.append(name)
    agentRecord['names'] = names
    agentRecord['publish'] = True
    agentRecord['jsonmodel_type'] = 'agent_corporate_entity'
    agentRecord = json.dumps(agentRecord)
    post = requests.post(baseURL + '/agents/corporate_entities', headers=headers, data=agentRecord).json()
    print json.dumps(post)
    uri = post['uri']
    f.writerow([row['sortName']]+[uri])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
