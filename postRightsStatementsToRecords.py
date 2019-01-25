import json
import requests
import secrets
import time
import csv
import argparse
from datetime import datetime

def createRightsStatement (rightsScenario):
    rights_statements = []
    rights_statement = {}
    rights_statement['rights_type'] = 'copyright'
    rights_statement['status'] = rightsScenario['status']
    rights_statement['start_date'] = date
    rights_statement['jurisdiction'] = 'US'
    rights_statement['publish'] = True
    rights_statement['jsonmodel_type'] = 'rights_statement'
    if rightsScenario.get('title') != None:
        external_documents = []
        external_document = {}
        external_document['title'] = rightsScenario['title']
        external_document['location'] = rightsScenario['location']
        external_document['identifier_type'] = 'uri'
        external_document['publish'] = True
        external_document['jsonmodel_type'] = 'rights_statement_external_document'
        external_documents.append(external_document)
        rights_statement['external_documents'] = external_documents
    notes = []
    note = {}
    note['type'] = 'additional_information'
    note['content'] = rightsScenario['content']
    note['publish'] = True
    note['jsonmodel_type'] = 'note_rights_statement'
    notes.append(note)
    rights_statement['notes'] = notes
    rights_statements.append(rights_statement)
    updatedAsRecord['rights_statements'] = rights_statements

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

noCR = {'status':'public_domain', 'title':'No Copyright - United States', 'location':'http://rightsstatements.org/page/NoC-US/1.0/', 'content':['No known copyright restrictions.']}
ARR = {'status':'copyrighted', 'content':['All rights reserved.']}

resourceUris = ['']

for resourceUri in resourceUris:
    asRecord = requests.get(baseURL+resourceUri, headers=headers).json()
    updatedAsRecord = asRecord
    date = datetime.today().strftime('%Y-%m-%d')
    createRightsStatement(noCR)
    updatedAsRecord = json.dumps(updatedAsRecord)
    post = requests.post(baseURL+resourceUri, headers=headers, data=updatedAsRecord).json()
    print(post)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
