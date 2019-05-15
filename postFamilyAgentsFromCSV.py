import json
import requests
import csv
import time
from datetime import datetime

secretsVersion = input('To edit production server, enter the name of the \
secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__('secrets')
        print('Editing Development')
else:
    print('Editing Development')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

targetFile = input('Enter file name: ')

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('postNewFamilyAgents' + date + '.csv', 'w'))
f.writerow(['sortName'] + ['uri'])

csvfile = csv.DictReader(open(targetFile))

for row in csvfile:
    agentRecord = {}
    names = []
    name = {}
    name['family_name'] = row['sortName']
    name['sort_name'] = row['sortName']
    name['jsonmodel_type'] = 'name_family'
    name['name_order'] = 'direct'
    name['rules'] = 'rda'
    try:
        name['dates'] = row['dates']
    except ValueError:
        pass
    try:
        name['qualifier'] = row['qualifier']
    except ValueError:
        pass
    names.append(name)
    if row['dates'] != '':
        dates = []
        date = {}
        date['label'] = 'existence'
        date['jsonmodel_type'] = 'date'
        if row['begin'] != '' and row['end'] != '':
            date['begin'] = row['begin']
            date['end'] = row['end']
            date['date_type'] = 'range'
        elif row['begin'] != '':
            date['begin'] = row['begin']
            date['date_type'] = 'single'
        elif row['end'] != '':
            date['end'] = row['end']
            date['date_type'] = 'single'
        dates.append(date)
        agentRecord['dates_of_existence'] = dates

    agentRecord['names'] = names
    agentRecord['publish'] = True
    agentRecord['jsonmodel_type'] = 'agent_family'
    agentRecord = json.dumps(agentRecord)
    print(agentRecord)
    post = requests.post(baseURL + '/agents/families', headers=headers,
                         data=agentRecord).json()
    print(json.dumps(post))
    uri = post['uri']
    f.writerow([row['sortName']] + [uri])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
