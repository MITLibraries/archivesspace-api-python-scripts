import json
import requests
import secrets
import time
import csv
from datetime import datetime

def addUriLink (key, valueSource):
    uri = '/repositories/3/resources/'+row['ResourceUri']
    value = row[valueSource]
    print value
    asRecord = requests.get(baseURL+uri, headers=headers).json()
    updatedRecord = asRecord
    if key == 'subjects':
        subjects = updatedRecord['subjects']
        originalSubjects = updatedRecord['subjects']
        subject = {}
        subject['ref'] = value
        if subject not in subjects:
            subjects.append(subject)
            updatedRecord['subjects'] = subjects
            print updatedRecord['subjects']
            updatedRecord = json.dumps(updatedRecord)
            print baseURL + uri
            post = requests.post(baseURL + uri, headers=headers, data=updatedRecord).json()
            print post
            f.writerow([uri]+[subjects]+[post])
        else:
            print 'no update'
            f.writerow([uri]+['no update']+[])
    elif key == 'linked_agents':
        agents = updatedRecord['linked_agents']
        print 'originalAgents'
        print agents
        originalAgents = updatedRecord['linked_agents']
        agent = {}
        agent['terms'] = []
        agent['ref'] = value
        if row['tag'].startswith('1'):
            agent['role'] = 'creator'
        elif row['tag'].startswith('7'):
            agent['role'] = 'creator'
        elif row['tag'].startswith('6'):
            agent['role'] = 'subject'
        else:
            'print error'
            f.writerow([uri]+['tag error']+[])
        if agent not in agents:
            agents.append(agent)
            print 'updatedAgents'
            print agents
            updatedRecord['linked_agents'] = agents
            updatedRecord = json.dumps(updatedRecord)
            print baseURL + uri
            post = requests.post(baseURL + uri, headers=headers, data=updatedRecord).json()
            print post
            f.writerow([uri]+[agents]+[post])
        else:
            print 'no update'
            print agent
            f.writerow([uri]+['no update']+[])
    else:
        'print error'
        f.writerow([uri]+['error']+[])

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

filename = raw_input('Enter filename (including \'.csv\'): ')

f=csv.writer(open(filename+'Post'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['uri']+['links']+['post'])

with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        addUriLink ('linked_agents', 'agentUri')
        #addUriLink ('subjects', 'SubjectUri')
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
