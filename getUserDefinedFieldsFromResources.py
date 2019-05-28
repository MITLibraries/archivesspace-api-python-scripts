import json
import requests
import secrets
import time
import csv

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

endpoint = '/repositories/'+repository+'/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f=csv.writer(open('UserDefinedFieldsFromResources.csv', 'w'))
f.writerow(['title']+['uri']+['bibnum']+['accessionAcknowledged']+['selector']+['assignedTo']+['appraisalLegacy']+['custodialHistory']+['electronicRecordLog']+['relatedMaterialsNote']+['archiveItSeeds']+['appraisal']+['accessionStatus'])

total_resources = len(ids)
total_accessions = len(ids)
for id in ids:
    print('id', id, total_resources, 'resource records remaining')
    total_resources= total_resources - 1
    endpoint = '/repositories/'+repository+'/resources/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    title = output['title']
    uri = output['uri']
    try:
        bibnum = output['user_defined']['real_1']
    except:
        bibnum = ''
    try:
        accessionAcknowledged = output['user_defined']['string_1']
    except:
        accessionAcknowledged = ''
    try:
        selector = output['user_defined']['string_2']
    except:
        selector = ''
    try:
        assignedTo = output['user_defined']['string_3']
    except:
        assignedTo = ''
    try:
        appraisalLegacy = output['user_defined']['string_4']
    except:
        appraisalLegacy = ''
    try:
        custodialHistory = output['user_defined']['text_1']
    except:
        custodialHistory = ''
    try:
        electronicRecordLog = output['user_defined']['text_2']
    except:
        electronicRecordLog = ''
    try:
        relatedMaterialsNote = output['user_defined']['text_3']
    except:
        relatedMaterialsNote = ''
    try:
        archiveItSeeds = output['user_defined']['text_4']
    except:
        archiveItSeeds = ''
    try:
        appraisal = output['user_defined']['text_5']
    except:
        appraisal = ''
    try:
        accessionStatus = output['user_defined']['enum_1']
    except:
        accessionStatus = ''
    if accessionAcknowledged or selector or assignedTo or appraisalLegacy or custodialHistory or electronicRecordLog or relatedMaterialsNote or archiveItSeeds or appraisal or accessionStatus:
        f.writerow([title]+[uri]+[bibnum]+[accessionAcknowledged]+[selector]+[assignedTo]+[appraisalLegacy]+[custodialHistory]+[electronicRecordLog]+[relatedMaterialsNote]+[archiveItSeeds]+[appraisal]+[accessionStatus])

for id in ids:
    print('id', id, total_accessions, 'accession records remaining')
    total_accessions = total_accessions - 1
    endpoint = '/repositories/'+repository+'/accessions/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    title = output['title']
    uri = output['uri']
    try:
        bibnum = output['user_defined']['real_1']
    except:
        bibnum = ''
    try:
        accessionAcknowledged = output['user_defined']['string_1']
    except:
        accessionAcknowledged = ''
    try:
        selector = output['user_defined']['string_2']
    except:
        selector = ''
    try:
        assignedTo = output['user_defined']['string_3']
    except:
        assignedTo = ''
    try:
        appraisalLegacy = output['user_defined']['string_4']
    except:
        appraisalLegacy = ''
    try:
        custodialHistory = output['user_defined']['text_1']
    except:
        custodialHistory = ''
    try:
        electronicRecordLog = output['user_defined']['text_2']
    except:
        electronicRecordLog = ''
    try:
        relatedMaterialsNote = output['user_defined']['text_3']
    except:
        relatedMaterialsNote = ''
    try:
        archiveItSeeds = output['user_defined']['text_4']
    except:
        archiveItSeeds = ''
    try:
        appraisal = output['user_defined']['text_5']
    except:
        appraisal = ''
    try:
        accessionStatus = output['user_defined']['enum_1']
    except:
        accessionStatus = ''
    if accessionAcknowledged or selector or assignedTo or appraisalLegacy or custodialHistory or electronicRecordLog or relatedMaterialsNote or archiveItSeeds or appraisal or accessionStatus:
        f.writerow([title]+[uri]+[bibnum]+[accessionAcknowledged]+[selector]+[assignedTo]+[appraisalLegacy]+[custodialHistory]+[electronicRecordLog]+[relatedMaterialsNote]+[archiveItSeeds]+[appraisal]+[accessionStatus])


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
