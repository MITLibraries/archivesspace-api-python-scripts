import json
import requests
import secrets
import argparse
import urllib3

secretsVersion = input('To edit production server, enter secrets file name: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--uri', help='URI of the object to retreive.')
args = parser.parse_args()

if args.uri:
    uri = args.uri
else:
    uri = input('Enter handle (\'/repositories/3/resources/855\'): ')

uri = '/repositories/3/archival_objects/215717'
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository
verify = secrets.verify

auth = requests.post(baseURL+'/users/'+user+'/login?password='+password, verify=verify).json()
session = auth['session']
print('Session: '+session)
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}

print(baseURL+uri)
output = requests.get(baseURL+uri, headers=headers, verify=verify).json()
uri = uri.replace('/repositories/'+repository+'/', '').replace('/', '-')
f = open(uri+'.json', 'w')
results = (json.dump(output, f))
f.close()
