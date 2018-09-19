import json
import requests
import secrets
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--uri', help='URI of the object to retreive. optional - if not provided, the script will ask for input')

args = parser.parse_args()

if args.uri:
    uri = args.uri
else:
    uri = raw_input('Enter handle (\'/repositories/3/resources/564\'): ')

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

print baseURL+uri
output = requests.get(baseURL + uri, headers=headers).json()
uri = uri.replace('/repositories/3/','').replace('/','-')
f=open(uri+'.json', 'w')
results=(json.dump(output, f))
f.close()
