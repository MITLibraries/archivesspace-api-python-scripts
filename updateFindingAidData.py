import json
import requests
import secrets
import csv

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

f=csv.writer(open('findingAidTitle.csv', 'wb'))
f.writerow(['uri']+['findingAidTitleProposed']+['findingAidTitleActual'])

f2=csv.writer(open('findingAidLanguage.csv', 'wb'))
f2.writerow(['uri']+['language'])

endpoint = '/repositories/3/resources/533'

output = requests.get(baseURL + endpoint, headers=headers).json()
eadID = output['id_0']
try:
    id1 = '.'+output['id_1']
except:
    id1=''
try:
    id2 = '.'+output['id_2']
except:
    id2 = ''
try:
    id3 = '.'+output['id_3']
except:
    id3=''
try:
    findingAidLanguage = output['finding_aid_language']
except:
    findingAidLanguage = ''
eadID = eadID+id1+id2+id3
f2.writerow([output['uri']]+[findingAidLanguage])
output['ead_id'] = eadID
output['ead_location'] = 'http://aspace.library.jhu.edu'+output['uri']
output['finding_aid_language'] = 'English'
f.writerow([output['uri']]+['Guide to the '+output['title']])
asRecord = json.dumps(output)
post = requests.post(baseURL + uri, headers=headers, data=asRecord).json()
print post
