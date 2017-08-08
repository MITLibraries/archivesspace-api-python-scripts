import json
import requests
import secrets
import time
import csv

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/3/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f=csv.writer(open('topContainerCountByResourceNoAOs.csv', 'wb'))
f.writerow(['title']+['uri']+['id_0']+['id_1']+['id_2']+['id_3']+['topContainerCount'])

f2=csv.writer(open('topContainersLinksNoAOs.csv', 'wb'))
f2.writerow(['resourceUri']+['topContainerUri'])

uniqueTopContainers = []
topContainerLinks = []
for id in ids:
    endpoint = '/repositories/3/resources/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    topContainersByResource = []
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
    try:
        instances = output['instances']
        for instance in instances:
            try:
                topContainer = instance['sub_container']['top_container']['ref']
                topContainersByResource.append(topContainer)
            except:
                print id, 'No top containers'
    except:
        pass
    for topContainer in topContainersByResource:
        topContainerLink = str(id) +'|'+topContainer
        if topContainerLink not in topContainerLinks:
            topContainerLinks.append(topContainerLink)
        if topContainer not in uniqueTopContainers:
            uniqueTopContainers.append(topContainer)
    topContainerCountByResource = len(topContainersByResource)
    f.writerow([title]+[uri]+[id0]+[id1]+[id2]+[id3]+[topContainerCountByResource])
    print id, len(uniqueTopContainers)

for topContainerLink in topContainerLinks:
    f2.writerow([topContainerLink[:topContainerLink.index('|')]]+[topContainerLink[topContainerLink.index('|')+1:]])

f3=csv.writer(open('uniqueTopContainersNoAOs.csv', 'wb'))
f3.writerow(['topContainer'])
for topContainer in uniqueTopContainers:
    f3.writerow([topContainer])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
