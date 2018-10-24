import json
import requests
import secrets
import time
import csv

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Development'
else:
    print 'Editing Development'

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/3/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f=csv.writer(open('topContainerCountByResource.csv', 'wb'))
f.writerow(['title']+['uri']+['id_0']+['id_1']+['id_2']+['id_3']+['topContainerCount'])

f2=csv.writer(open('topContainersLinks.csv', 'wb'))
f2.writerow(['resourceUri']+['topContainerUri'])

f3=csv.writer(open('uniqueTopContainers.csv', 'wb'))
f3.writerow(['topContainer']+['indicator']+['barcode'])


total = len(ids)
topContainerLinks = []
uniqueTopContainers = []
for id in ids:

    resourceTopContainers = []
    print 'id', id, total, 'records remaining'
    total = total - 1
    endpoint = '/repositories/3/resources/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    title = output['title'].encode('utf-8')
    uri = output['uri']
    id0 = output['id_0']
    try:
        id1 = output['id_1']
    except:
        id1=''
    try:
        id2 = output['id_2']
    except:
        id2 = ''
    try:
        id3 = output['id_3']
    except:
        id3=''
    # ###searchEndpoint = '/repositories/3/top_containers/search'
    # ###output = requests.get(baseURL + searchEndpoint, headers=headers).json()
    page = 1
    payload = {'page': page, 'page_size': '3000', 'root_record': endpoint}
    search = requests.get(baseURL+'/search', headers=headers, params=payload).json()
    results = []
    resultsPage = search['results']
    for result in resultsPage:
        results.append(result)
    while resultsPage != []:
        page = page + 1
        payload = {'page': page, 'page_size': '3000', 'root_record': endpoint}
        search = requests.get(baseURL+'/search', headers=headers, params=payload).json()
        resultsPage = search['results']
        for result in resultsPage:
            results.append(result)

    for result in results:
        try:
            topContainers = result['top_container_uri_u_sstr']
            for topContainer in topContainers:
                if topContainer not in resourceTopContainers:
                    resourceTopContainers.append(topContainer)
                if topContainer not in uniqueTopContainers:
                    uniqueTopContainers.append(topContainer)
                topContainerLink = str(id)+'|'+topContainer
                if topContainerLink not in topContainerLinks:
                    topContainerLinks.append(topContainerLink)
        except:
            topContainers = []
    topContainerCount = len(resourceTopContainers)
    print 'top containers', topContainerCount
    f.writerow([title]+[uri]+[id0]+[id1]+[id2]+[id3]+[topContainerCount])

for topContainerLink in topContainerLinks:
    f2.writerow([topContainerLink[:topContainerLink.index('|')]]+[topContainerLink[topContainerLink.index('|')+1:]])

for topContainer in uniqueTopContainers:
        search = requests.get(baseURL+topContainer, headers=headers).json()
        try:
            indicator = search['indicator']
        except:
            indicator = ''

        try:
            barcode = search['barcode']
        except:
            barcode = ''
        f3.writerow([topContainer]+[indicator]+[barcode])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
