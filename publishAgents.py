import json
import requests
import time
import csv
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
    secrets = __import__('secrets')
    print('Editing Development')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()

session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

agentTypes = ['people', 'families', 'corporate_entities', 'software']

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('publishedAgents' + date + '.csv', 'w'))
f.writerow(['uri'] + ['post'])
f2 = csv.writer(open('errorsAgents' + date + '.csv', 'w'))
f2.writerow(['uri'] + ['post'])

for agentType in agentTypes:
    endpoint = '/agents/' + agentType + '?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    counter = 0
    for id in ids:
        counter += 1
        print(counter)
        id = str(id)
        print(baseURL + '/agents/' + agentType + '/' + id)
        output = requests.get(baseURL + '/agents/' + agentType + '/' + id,
                              headers=headers)

        output = output.json()
        output['publish'] = True
        asRecord = json.dumps(output)
        post = requests.post(baseURL + '/agents/' + agentType + '/' + id,
                             headers=headers, data=asRecord)
        print(post.status_code)
        if post.status_code != 200:
            f2.writerow([id] + [post])
            print('error')
        else:
            post = post.json()
            post = json.dumps(post)
            print(post)
            f.writerow(['/agents/' + agentType + '/' + id]
                       + [post])
            print('row written - updated')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
