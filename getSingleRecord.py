import json
import requests
import secrets
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

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--uri', help='URI of the object to retreive. optional - if not provided, the script will ask for input')

args = parser.parse_args()

# if args.uri:
#     uri = args.uri
# else:
#     uri = raw_input('Enter handle (\'/repositories/3/resources/855\'): ')

uri = '/repositories/3/digital_objects/141'
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL+'/users/'+user+'/login?password='+password).json()
session = auth['session']
print(auth)
print(session)
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}

print(baseURL+uri)
output = requests.get(baseURL + uri, headers=headers).json()
uri = uri.replace('/repositories/'+repository+'/', '').replace('/', '-')
f = open(uri+'.json', 'w')
results = (json.dump(output, f))
f.close()
