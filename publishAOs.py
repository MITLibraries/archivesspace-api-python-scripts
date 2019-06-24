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
print(session)
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('publishedAOs' + date + '.csv', 'w'))
f.writerow(['uri'] + ['title'] + ['level'] + ['post'])
date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f2 = csv.writer(open('errorsAOs' + date + '.csv', 'w'))
f2.writerow(['uri'] + ['post'])

page = 0

results = ''
while results != []:
    page += 1
    endpoint = ('search?q=*&page=' + str(page)
                + '&page_size=100&type[]=archival_object')
    output = requests.get(baseURL + '/repositories/2/' + endpoint,
                          headers=headers).json()
    results = output['results']
    print(output['last_page'] - output['this_page'], output['total_hits'])
    for result in results:
        aoUri = result['uri']
        aoTitle = result['title']
        jsonString = json.loads(result['json'])
        publish = jsonString['publish']
        level = jsonString['level']
        if publish is not True:
            output = requests.get(baseURL + aoUri, headers=headers)
            output = output.json()
            updatedAO = output
                updatedAO['publish'] = True
                updatedAO = json.dumps(updatedAO)
                aoPost = requests.post(baseURL + aoUri,
                                       headers=headers,
                                       data=updatedAO)
                print(aoPost.status_code)
                if aoPost.status_code != 200:
                    f2.writerow([aoUri] + [aoTitle] + [level] + [aoPost])
                    print('error')
                else:
                    aoPost = aoPost.json()
                    aoPost = json.dumps(aoPost)
                    print(aoUri, aoTitle, level, aoPost)
                    f.writerow([aoUri] + [aoTitle] + [level] + [aoPost])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
