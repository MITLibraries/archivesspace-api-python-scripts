import json
import requests
import secrets
import time
import csv
import argparse
from datetime import datetime

#functions
def createRightsStatement (rightsProfile):
    rightsProfile = eval(rightsProfile)
    rights_statements = []
    rights_statement = {}
    rights_statement['rights_type'] = 'copyright'
    rights_statement['status'] = rightsProfile['status']
    rights_statement['start_date'] = startDate
    rights_statement['determination_date'] = determinationDate
    rights_statement['jurisdiction'] = 'US'
    rights_statement['publish'] = True
    rights_statement['jsonmodel_type'] = 'rights_statement'
    if rightsProfile.get('title') != None:
        external_documents = []
        external_document = {}
        external_document['title'] = rightsProfile['title']
        external_document['location'] = rightsProfile['location']
        external_document['identifier_type'] = 'uri'
        external_document['publish'] = True
        external_document['jsonmodel_type'] = 'rights_statement_external_document'
        external_documents.append(external_document)
        rights_statement['external_documents'] = external_documents
    notes = []
    note = {}
    note['type'] = 'additional_information'
    note['content'] = rightsProfile['content']
    note['publish'] = True
    note['jsonmodel_type'] = 'note_rights_statement'
    notes.append(note)
    rights_statement['notes'] = notes
    rights_statements.append(rights_statement)
    updatedAsRecord['rights_statements'] = rights_statements

#selects prod or dev server by selecting appropriate secrets.py file
secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

#command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='the CSV file of record URIs and corresponding rights profiles. optional - if not provided, the script will ask for input')

args = parser.parse_args()

if args.file:
    file = args.file
else:
    file = input('Enter the CSV file of records URIs and corresponding rights profiles')

#run time start, load secrets.py variables, and authenticate
startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

#rights profiles
noCR = {'status':'public_domain', 'title':'No Copyright - United States', 'location':'http://rightsstatements.org/page/NoC-US/1.0/', 'content':['No known copyright restrictions.']}
ARR = {'status':'copyrighted', 'content':['All rights reserved.']}

#script content
csvfile = csv.DictReader(open(file))

for row in csvfile:
    resourceUri = row['recordUri']
    rightsProfile = row['rightsProfile']
    startDate = row['startDate']
    determinationDate = datetime.today().strftime('%Y-%m-%d')
    asRecord = requests.get(baseURL+resourceUri, headers=headers).json()
    updatedAsRecord = asRecord
    print(rightsProfile)
    createRightsStatement(rightsProfile)
    updatedAsRecord = json.dumps(updatedAsRecord)
    post = requests.post(baseURL+resourceUri, headers=headers, data=updatedAsRecord).json()
    print(post)

#print script run time
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
