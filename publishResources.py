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

endpoint = '/repositories/' + repository + '/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('publishedResources' + date + '.csv', 'w'))
f.writerow(['uri'] + ['post'])
date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f2 = csv.writer(open('errorsResources' + date + '.csv', 'w'))
f2.writerow(['uri'] + ['post'])

skippedResources = ['AC-0026', 'AC-0067', 'AC-0094', 'AC-0103', 'AC-0126',
                    'AC-0155', 'AC-0178', 'AC-0227', 'AC-0241', 'AC-0248',
                    'AC-0249', 'AC-0251', 'AC-0253', 'AC-0255', 'AC-0257',
                    'AC-0258', 'AC-0263', 'AC-0284', 'AC-0296', 'AC-0322',
                    'AC-0356', 'AC-0372', 'AC-0374', 'AC-0375', 'AC-0376',
                    'AC-0396', 'AC-0403', 'AC-0407', 'AC-0409', 'AC-0411',
                    'AC-0424', 'AC-0429', 'AC-0431', 'AC-0437', 'AC-0439',
                    'AC-0440', 'AC-0443', 'AC-0444', 'AC-0446', 'AC-0460',
                    'AC-0463', 'AC-0471', 'AC-0472', 'AC-0492', 'AC-0504',
                    'AC-0511', 'AC-0512', 'AC-0558', 'AC-0565', 'AC-0593',
                    'AC-0594', 'AC-0607', 'AC-0612', ' AC-0643']

disclaimer = ('Some collection descriptions are based on legacy data and may '
              'be incomplete or contain inaccuracies. Description may change '
              'pending verification. Please contact the MIT Department of '
              'Distinctive Collections if you notice any errors or '
              'discrepancies.')

print(len(ids))
counter = 0
for id in ids:
    counter += 1
    print(counter)
    id = str(id)
    print(baseURL + '/repositories/' + repository
          + '/resources/' + id)
    output = requests.get(baseURL + '/repositories/' + repository
                          + '/resources/' + id, headers=headers)

    output = output.json()

    id_0 = output.get('id_0', '')
    id_1 = output.get('id_1', '')
    if id_1 != '':
        id_1 = '-' + id_1
    id_2 = output.get('id_2', '')
    if id_2 != '':
        id_2 = '-' + id_2
    id_3 = output.get('id_3', '')
    if id_3 != '':
        id_3 = '-' + id_3
    resConCatID = id_0 + id_1 + id_2 + id_3
    if resConCatID not in skippedResources:
        if output['publish'] is False:
            output['publish'] = True
            editedNotes = output['notes']
            for note in editedNotes:
                processinfoExists = False
                if 'type' in note:
                    if note['type'] == 'processinfo':
                        editedSubnotes = note['subnotes']
                        for subnote in editedSubnotes:
                            subnote['publish'] = False
                    elif note['type'] == 'acqinfo':
                        if note['publish'] is True:
                            note['publish'] = False
            discProcNote = {}
            discProcNote['type'] = 'processinfo'
            discProcNote['label'] = 'Processing Information note'
            discProcNote['publish'] = True
            discProcNote['jsonmodel_type'] = 'note_multipart'
            discSubnote = {}
            discSubnote['content'] = (disclaimer)
            discSubnote['publish'] = True
            discSubnote['jsonmodel_type'] = 'note_text'
            discProcNote['subnotes'] = [discSubnote]
            editedNotes.append(discProcNote)

            output['notes'] = editedNotes
            asRecord = json.dumps(output)
            post = requests.post(baseURL + '/repositories/' + repository
                                 + '/resources/' + id, headers=headers,
                                 data=asRecord)
            print(post.status_code)
            if post.status_code != 200:
                f2.writerow([id] + [post])
                print('error')
            else:
                post = post.json()
                post = json.dumps(post)
                print(post)
                f.writerow(['/repositories/' + repository + '/resources/' + id]
                           + [post])
                print('row written - updated')

        else:
            f.writerow([id] + ['already published'] + [counter])
            print('row written - already published')
    else:
        f.writerow([id] + ['skipped'] + [counter])
        print('row written - skipped collection')


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
