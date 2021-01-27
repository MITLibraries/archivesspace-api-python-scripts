import json
import requests
from datetime import datetime
import time
import argparse
import secrets
import pandas as pd
import urllib3

startTime = time.time()

secretsVersion = input('To edit production server, enter secrets filename: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

# import secrets
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repo = secrets.repository
verify = secrets.verify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='filename to retreive')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter file name as filename.csv: ')

# authenticate
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password,
                     verify=verify).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

df = pd.read_csv(filename)

log = []
for count, row in df.iterrows():
    itemLog = {}
    archival_object = row['archival_object']
    uri = row['uri']
    print(count, archival_object)
    itemLog['archival_object'] = archival_object
    aobject = requests.get(baseURL+archival_object, headers=headers,
                           verify=verify).json()
    instance = {'instance_type': 'digital_object', 'jsonmodel_type': 'instance',
                'is_representative': False,
                'digital_object': {'ref': uri}}
    list = aobject.get('instances')
    if list:
        list.append(instance)
        aobject['instances'] = list
    else:
        aobject['instances'] = [instance]
    print(aobject)
    aobject = json.dumps(aobject)
    post = requests.post(baseURL+archival_object, headers=headers,
                         verify=verify, data=aobject).json()
    itemLog['post'] = post
    log.append(itemLog)

log = pd.DataFrame.from_dict(log)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
log.to_csv('logOfUpdatedAO_'+dt+'.csv')

# Show script runtime
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Post complete.  Total script run time: ', '%d:%02d:%02d' % (h, m, s))
