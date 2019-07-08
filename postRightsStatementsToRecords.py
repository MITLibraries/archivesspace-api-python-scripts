import json
import requests
import time
import csv
import argparse
from datetime import datetime


# functions
def createRightsStatement(rightsProfile):
    """Create rights statement based on the specified rights profile."""
    rightsProfile = eval(rightsProfile)
    rights_statements = []
    rights_statement = {}
    rights_statement['rights_type'] = 'copyright'
    rights_statement['status'] = rightsProfile['status']
    rights_statement['start_date'] = startDate
    rights_statement['jurisdiction'] = 'US'
    rights_statement['publish'] = True
    rights_statement['jsonmodel_type'] = 'rights_statement'
    if rightsProfile.get('title') is not None:
        external_documents = []
        external_document = {}
        external_document['title'] = rightsProfile['title']
        external_document['location'] = rightsProfile['location']
        external_document['identifier_type'] = 'uri'
        external_document['publish'] = True
        external_document['jsonmodel_type'] = \
            'rights_statement_external_document'
        external_documents.append(external_document)
        rights_statement['external_documents'] = external_documents
    notes = []
    note = {}
    note['type'] = 'additional_information'
    note['publish'] = True
    note['jsonmodel_type'] = 'note_rights_statement'
    if row['notesText'] != '':
        note['content'] = [row['notesText']]
        notes.append(note)
        rights_statement['notes'] = notes
    elif 'content' in rightsProfile:
        note['content'] = [rightsProfile['content']]
        notes.append(note)
        rights_statement['notes'] = notes
    else:
        pass
    rights_statements.append(rights_statement)
    external_documents = ''
    notes = ''
    updatedAsRecord['rights_statements'] = rights_statements


def findKey(d, key):
    """Find all instances of key."""
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j


# rights profiles
PDNC = {'status': 'public_domain', 'title': 'No Copyright - United States',
        'location': 'http://rightsstatements.org/page/NoC-US/1.0/'}
PDCR = {'status': 'public_domain', 'title':
        'No Copyright - Contractual Restrictions',
        'location': 'http://rightsstatements.org/page/NoC-CR/1.0/'}
MITCCBYNC = {'status': 'copyrighted', 'title':
             'Creative Commons Attribution-NonCommercial 4.0 International'
             '(CC BY-NC 4.0)', 'location':
             'https://creativecommons.org/licenses/by-nc/4.0/'}
MITCRNC = {'status': 'copyrighted', 'title':
           'In Copyright - Non-Commercial Use Permitted', 'location':
           'http://rightsstatements.org/vocab/InC-NC/1.0/'}
CC0 = {'status': 'public_domain', 'title':
       'Creative Commons CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
       'location': 'https://creativecommons.org/publicdomain/zero/1.0/'}
MITCREU = {'status': 'copyrighted', 'title':
           'In Copyright - Educational Use Permitted', 'location':
           'http://rightsstatements.org/page/InC-EDU/1.0/'}
LBDDT = {'status': 'copyrighted'}
LBDARR = {'status': 'copyrighted', 'content': 'All rights reserved.'}
LBCEMITU = {'status': 'copyrighted', 'content': 'Licensed for educational and '
            'research use by the MIT community only.'}
LBCECREU = {'status': 'copyrighted', 'title':
            'In Copyright - Educational Use Permitted', 'location':
            'http://rightsstatements.org/page/InC-EDU/1.0/'}
LBCECRNC = {'status': 'copyrighted', 'title':
            'In Copyright - Non-Commercial Use Permitted', 'location':
            'http://rightsstatements.org/vocab/InC-NC/1.0/'}
LBCECR = {'status': 'public_domain', 'title':
          'No Copyright - Contractual Restrictions',
          'location': 'http://rightsstatements.org/page/NoC-CR/1.0/'}
CR3ARR = {'status': 'copyrighted', 'content': ['All rights reserved.']}
CR3UCR = {'status': 'unknown', 'title':
          'In Copyright - Rights-Holder(s) Unlocatable Or Unidentifiable',
          'location': 'http://rightsstatements.org/vocab/InC-RUU/1.0/'}
NKCR = {'status': 'unknown', 'title': 'No Known Copyright',
        'location': 'http://rightsstatements.org/page/NKC/1.0/'}
CRNE = {'status': 'unknown', 'title': 'Copyright Not Evaluated',
        'location': 'http://rightsstatements.org/vocab/CNE/1.0/'}
CRUD = {'status': 'unknown', 'title': 'Copyright Undetermined', 'location':
        'http://rightsstatements.org/page/UND/1.0/'}
CRNC = {'status': 'unknown', 'title': 'Copyright Not Evaluated',
        'location': 'http://rightsstatements.org/vocab/CNE/1.0/',
        'content': 'Copyright not evaluated. Please see the collection '
        'overview for additional information.'}
CRNS = {'status': 'unknown', 'title': 'Copyright Not Evaluated',
        'location': 'http://rightsstatements.org/vocab/CNE/1.0/',
        'content': 'Copyright not evaluated. Please see the series-level '
        'overview for additional information.'}
CRNO = {'status': 'unknown'}

# selects prod or dev server by selecting appropriate secrets.py file
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

# command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='the CSV file of record URIs and \
corresponding rights profiles. optional - if not provided, the script \
will ask for input')

args = parser.parse_args()

if args.file:
    file = args.file
else:
    file = input('Enter the CSV file of records URIs and corresponding \
    rights profiles')

# run time start, load secrets.py variables, and authenticate
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

print(baseURL)

# iterate through csv
csvfile = csv.DictReader(open(file))

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('rightsStatementsAdded' + date + '.csv', 'w'))
f.writerow(['uri'] + ['post'])

for row in csvfile:
    recordUri = row['recordUri']
    rightsProfile = row['rightsProfile']
    startDate = datetime.today().strftime('%Y-%m-%d')
    asRecord = requests.get(baseURL + recordUri, headers=headers).json()
    updatedAsRecord = asRecord
    print(rightsProfile)
    createRightsStatement(rightsProfile)
    updatedAsRecord = json.dumps(updatedAsRecord)
    post = requests.post(baseURL + recordUri, headers=headers,
                         data=updatedAsRecord).json()
    f.writerow([recordUri] + [post])
    print(post)

    output = requests.get(baseURL + recordUri + '/tree',
                          headers=headers).json()

    for aoUri in findKey(output, 'record_uri'):
        if 'archival_objects' in aoUri:
            output = requests.get(baseURL + aoUri, headers=headers).json()
            updatedAsRecord = output
            rights_statements = []
            rights_statement = {}
            rights_statement['rights_type'] = 'copyright'
            rights_statement['status'] = 'unknown'
            rights_statement['start_date'] = startDate
            rights_statement['jurisdiction'] = 'US'
            rights_statement['publish'] = True
            rights_statement['jsonmodel_type'] = 'rights_statement'
            external_documents = []
            external_document = {}
            external_document['title'] = 'Copyright Not Evaluated'
            external_document['location'] = \
                'http://rightsstatements.org/vocab/CNE/1.0/'
            external_document['identifier_type'] = 'uri'
            external_document['publish'] = True
            external_document['jsonmodel_type'] = \
                'rights_statement_external_document'
            external_documents.append(external_document)
            rights_statement['external_documents'] = external_documents
            notes = []
            note = {}
            note['type'] = 'additional_information'
            note['publish'] = True
            note['jsonmodel_type'] = 'note_rights_statement'
            note['content'] = ['Copyright not evaluated. Please see the '
                               'collection overview for additional '
                               'information.']
            notes.append(note)
            rights_statement['notes'] = notes

            rights_statements.append(rights_statement)
            updatedAsRecord['rights_statements'] = rights_statements
            updatedAsRecord = json.dumps(updatedAsRecord)
            post = requests.post(baseURL + aoUri, headers=headers,
                                 data=updatedAsRecord).json()
            f.writerow([aoUri] + [post])
            print(post)

# print script run time
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
