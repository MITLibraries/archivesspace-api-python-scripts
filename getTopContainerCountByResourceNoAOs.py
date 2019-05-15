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

endpoint = '/repositories/' + repository + '/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f = csv.writer(open('topContainerCountByResourceNoAOs.csv', 'w'))
f.writerow(['title'] + ['uri'] + ['id_0'] + ['id_1'] + ['id_2'] + ['id_3']
           + ['topContainerCount'])

f2 = csv.writer(open('topContainersLinksNoAOs.csv', 'w'))
f2.writerow(['resourceUri'] + ['topContainerUri'])

uniqueTopContainers = []
topContainerLinks = []
for id in ids:
    endpoint = '/repositories/' + repository + '/resources/' + str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    topContainersByResource = []
    title = output['title']
    uri = output['uri']
    id0 = output['id_0']
    try:
        id1 = output['id_1']
    except ValueError:
        id1 = ''
    try:
        id2 = output['id_2']
    except ValueError:
        id2 = ''
    try:
        id3 = output['id_3']
    except ValueError:
        id3 = ''
    try:
        instances = output['instances']
        for instance in instances:
            try:
                topContainer = instance['sub_container']['top_container']
                topContainer = topContainer['ref']
                topContainersByResource.append(topContainer)
            except ValueError:
                print(id, 'No top containers')
    except ValueError:
        pass
    for topContainer in topContainersByResource:
        topContainerLink = str(id) + '|' + topContainer
        if topContainerLink not in topContainerLinks:
            topContainerLinks.append(topContainerLink)
        if topContainer not in uniqueTopContainers:
            uniqueTopContainers.append(topContainer)
    topContainerCountByResource = len(topContainersByResource)
    f.writerow([title] + [uri] + [id0] + [id1] + [id2] + [id3]
               + [topContainerCountByResource])
    print(id, len(uniqueTopContainers))

for topContainerLink in topContainerLinks:
    f2.writerow([topContainerLink[:topContainerLink.index('|')]]
                + [topContainerLink[topContainerLink.index('|') + 1:]])

f3 = csv.writer(open('uniqueTopContainersNoAOs.csv', 'w'))
f3.writerow(['topContainer'])
for topContainer in uniqueTopContainers:
    search = requests.get(baseURL + topContainer, headers=headers).json()
    try:
        indicator = search['indicator']
    except ValueError:
        indicator = ''
    try:
        barcode = search['barcode']
    except ValueError:
        barcode = ''
    f3.writerow([topContainer] + [indicator] + [barcode])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
