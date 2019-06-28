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
print(baseURL)

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()

session = auth['session']
print(session)
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('unpublishedNotesOnAOs' + date + '.csv', 'w'))
f.writerow(['uri'] + ['aoTitle'] + ['post'])
f2 = csv.writer(open('errorsUnpublishedNotesOnAOs' + date + '.csv', 'w'))
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
        notes = jsonString['notes']
        processinfo = False
        acqinfo = False
        for note in notes:
            if 'type' in note:
                if note['type'] == 'processinfo':
                    for subnote in note['subnotes']:
                        if subnote['publish'] is True:
                            processinfo = True
                elif note['type'] == 'acqinfo':
                    if note['publish'] is True:
                        acqinfo = True
        if processinfo is True or acqinfo is True:
            output = requests.get(baseURL + aoUri, headers=headers)
            output = output.json()
            updatedAO = output
            aoTitle = updatedAO['title']
            editedNotes = updatedAO['notes']
            for editedNote in editedNotes:
                postAO = False
                if 'type' in note:
                    if editedNote['type'] == 'processinfo':
                        editedSubnotes = editedNote['subnotes']
                        for editedSubnote in editedSubnotes:
                            if editedSubnote['publish'] is True:
                                editedSubnote['publish'] = False
                                postAO = True
                        editedNote['subnotes'] = editedSubnotes
                    elif editedNote['type'] == 'acqinfo':
                        if editedNote['publish'] is True:
                            editedNote['publish'] = False
                            postAO = True
            if postAO is True:
                updatedAO['notes'] = editedNotes
                updatedAO = json.dumps(updatedAO)
                aoPost = requests.post(baseURL + aoUri, headers=headers,
                                       data=updatedAO)
                print(aoPost.status_code)
                if aoPost.status_code != 200:
                    f2.writerow([id] + [aoPost])
                    print('error')
                else:
                    aoPost = aoPost.json()
                    aoPost = json.dumps(aoPost)
                    print(aoPost)
                    f.writerow([aoUri] + [aoTitle] + [aoPost])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
