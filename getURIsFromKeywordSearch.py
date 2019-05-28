import json
import requests
import secrets
import csv
import argparse

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

types = []

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--keyword', help='Keyword to retreive. optional - if not provided, the script will ask for input')
parser.add_argument('-t', '--type', choices=['accession', 'resource', 'subject', 'agent', 'location', 'archival_object'], help='What type of records do you want to search? Type out which of the following you want: accession, resource, subject, agent, location, archival_object. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.keyword:
    keyword = args.keyword
else:
    keyword = input('Enter keyword to search: ')
if args.type:
    type = args.type
    type = type.split(',')
    for item in type:
        item = item.strip()
        item = '&type[]='+item
        types.append(item)
else:
    type = input('What type of records do you want to search? Type out which of the following you want in a list: accession, resource, subject, agent, location, archival_object. ')
    type = type.split(',')
    for item in type:
        item = item.strip()
        item = '&type[]='+item
        types.append(item)

types = ''.join(types)
print(types)


baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}


endpoint = '/repositories/3/search?q='+keyword+types'&page_size=2000&page=1'

results = requests.get(baseURL + endpoint, headers=headers).json()
results = results['results']

f=csv.writer(open(keyword+'Search.csv', 'w'))
f.writerow(['uri'])

for result in results:
    uri = result['uri']
    f.writerow([uri])

print(len(results))
