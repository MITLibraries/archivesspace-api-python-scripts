import json
import requests
import secrets
import time
import csv
import argparse
from datetime import datetime

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Enter the name of the file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter the name of the file: ')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}


f = csv.writer(open('selectFieldsUpdate'+'Post'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f.writerow(['title']+['uri']+['finding_aid_title']+['ead_id']+['ead_url'])


with open(filename, encoding='utf-8') as changesFile:
    elements = csv.DictReader(changesFile)
    for element in elements:
        endpoint = element['uri'].strip()
        print(endpoint)
        try:
            output = requests.get(baseURL + endpoint, headers=headers).json()
        except:
            continue
            print('{} currently unavaible. Check to see if it exists'.format(endpoint))
            print('')
            f.writerow([endpoint]+['COULD NOT FIND RESOURCE'])
        try:
            title = output['title']
        except:
            title = ''
        try:
            uri = output['uri'].strip()
        except:
            uri = ''
        try:
            finding_aid_title = output['finding_aid_title']
        except:
            finding_aid_title = ''
        try:
            ead_id = output['ead_id']
        except:
            ead_id = ''
        try:
            ead_url = output['ead_location']
        except:
            ead_url = ''
        try:
            finding_aid_language = output['finding_aid_language']
        except:
            finding_aid_language = ''
        try:
            finding_aid_rules = output['finding_aid_description_rules']
        except:
            finding_aid_rules = ''
        f.writerow([title]+[uri]+[finding_aid_title]+[ead_id]+[ead_url]+[finding_aid_language]+[finding_aid_rules])
        print([title]+[uri]+[finding_aid_title]+[ead_id]+[ead_url]+[finding_aid_language]+[finding_aid_rules])
        new_finding_aid_title = element['findingAidTitleProposed'].strip()
        new_ead_id = element['eadID'].strip()
        new_ead_url = element['eadLocation'].strip()
        new_output = output
        change = 0
        if finding_aid_title != new_finding_aid_title:
            new_output['finding_aid_title'] = new_finding_aid_title
            change = change + 1
        else:
            pass
        if ead_id != new_ead_id:
            new_output['ead_id'] = new_ead_id
            change = change + 1
        else:
            pass
        if ead_url != new_ead_url:
            new_output['ead_location'] = new_ead_url
            change = change + 1
        else:
            pass
        if finding_aid_language != 'English':
            new_output['finding_aid_language'] = 'English'
            change = change + 1
        else:
            pass
        if finding_aid_rules != 'Describing Archives: A Content Standard':
            new_output['finding_aid_description_rules'] = 'Describing Archives: A Content Standard'
            change = change + 1
        else:
            pass
        if change != 0:
            finding_aid_title = new_output['finding_aid_title']
            ead_id = new_output['ead_id']
            ead_url = new_output['ead_location']
            finding_aid_language = new_output['finding_aid_language']
            finding_aid_rules = new_output['finding_aid_description_rules']
            f.writerow([title]+[uri]+[finding_aid_title]+[ead_id]+[ead_url]+[finding_aid_language]+[finding_aid_rules])
            print([title]+[uri]+[finding_aid_title]+[ead_id]+[ead_url]+[finding_aid_language]+[finding_aid_rules])
            post = requests.post(baseURL + uri, headers=headers, data=json.dumps(new_output))
            print(post)
            print('')
        else:
            print('{} skipped'.format(uri))
            print('')
            f.writerow([title]+[uri]+['no update'])


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
