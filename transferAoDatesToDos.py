import json
import requests
import time
import csv

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

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}
print('authenticated')

endpoint = '/repositories/' + repository + '/archival_objects?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()
ids.reverse()
print(len(ids))

# Generates a text file of AOs with DOs. Takes 2+ hours to generate so this
# code block is separate so the main portion of the script can be run
# more quickly.

# f = csv.writer(open('archivalObjectsWithDigitalObjects.csv', 'w'))
# f.writerow(['uri'])
# doAos = []
#
# for id in ids:
#     endpoint = '/repositories/'+repository+'/archival_objects/'+str(id)
#     output = requests.get(baseURL + endpoint, headers=headers).json()
#     try:
#         dates = output['dates']
#     except ValueError:
#         dates = ''
#     uri = output['uri']
#     instances = output['instances']
#     for instance in instances:
#         if instance['instance_type'] == 'digital_object':
#             doUri = instance['digital_object']['ref']
#             print(doUri)
#             f.writerow([uri])
#             doAos.append(uri)
#
# f2=open('archivalObjectsWithDigitalObjectsList.txt', 'w')
# f2.write(json.dumps(doAos))

f = csv.writer(open('DigitalObjectsDatesEdited.csv', 'w'))
f.writerow(['doUri'] + ['oldBegin'] + ['oldEnd'] + ['oldExpression']
           + ['oldLabel'] + ['aoUri'] + ['newBegin'] + ['newEnd']
           + ['newExpression'] + ['newLabel'] + ['post'])

doAos = json.load(open('archivalObjectsWithDigitalObjectsList.txt', 'r'))
for doAo in doAos:
    print(doAo)
    aoBegin = ''
    aoExpression = ''
    aoLabel = ''
    aoEnd = ''
    doBegin = ''
    doExpression = ''
    doLabel = ''
    doEnd = ''
    aoOutput = requests.get(baseURL + doAo, headers=headers).json()
    try:
        aoDates = aoOutput['dates']
        for aoDate in aoDates:
            try:
                aoBegin = aoDate['begin']
            except ValueError:
                aoBegin = ''
            try:
                aoEnd = aoDate['end']
            except ValueError:
                aoEnd = ''
            try:
                aoExpression = aoDate['expression']
            except ValueError:
                aoExpression = ''
            try:
                aoLabel = aoDate['label']
            except ValueError:
                aoLabel = ''
    except ValueError:
        aoBegin = ''
        aoExpression = ''
        aoLabel = ''
        aoEnd = ''
    try:
        instances = aoOutput['instances']
    except ValueError:
        continue
    for instance in instances:
        if instance['instance_type'] == 'digital_object':
            if aoBegin + aoExpression + aoLabel != '':
                doUri = instance['digital_object']['ref']
                doOutput = requests.get(baseURL
                                        + str(doUri), headers=headers).json()
                print('moving date from AO to DO')
                doDates = doOutput['dates']
                if doDates == []:
                    print('no date', doDates)
                    doBegin = ''
                    doExpression = ''
                    doLabel = ''
                    doEnd = ''
                    doDates = []
                    doDate = {}
                    doDate['begin'] = aoBegin
                    doDate['expression'] = aoExpression
                    doDate['label'] = aoLabel
                    doDate['date_type'] = 'single'
                    if aoEnd != '':
                        doDate['end'] = aoEnd
                        doDate['date_type'] = 'range'
                    doDates.append(doDate)
                    doOutput['dates'] = doDates
                    output = json.dumps(doOutput)
                    doPost = requests.post(baseURL + doUri, headers=headers,
                                           data=output).json()
                    print(doPost)
                else:
                    print('existing date', doDates)
                    for doDate in doDates:
                        try:
                            doBegin = doDate['begin']
                        except ValueError:
                            doBegin = ''
                        try:
                            doEnd = doDate['end']
                        except ValueError:
                            doEnd = ''
                        try:
                            doExpression = doDate['expression']
                        except ValueError:
                            doExpression = ''
                        try:
                            doLabel = doDate['label']
                        except ValueError:
                            doLabel = ''
                        if aoBegin != '':
                            doDate['begin'] = aoBegin
                        if aoExpression != '':
                            doDate['expression'] = aoExpression
                        if aoLabel != '':
                            doDate['label'] = aoLabel
                        if aoEnd != '':
                            doDate['end'] = aoEnd
                    doOutput['dates'] = doDates
                    output = json.dumps(doOutput)
                    doPost = requests.post(baseURL + doUri, headers=headers,
                                           data=output).json()
                    print(doPost)
                f.writerow([doUri] + [doBegin] + [doEnd] + [doExpression]
                           + [doLabel] + [doAo] + [aoBegin] + [aoEnd]
                           + [aoExpression] + [aoLabel] + [doPost])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
