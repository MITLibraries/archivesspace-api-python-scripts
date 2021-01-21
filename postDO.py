import json
import requests
from datetime import datetime
import time
import argparse
import secrets
import pandas as pd
import urllib3
import os

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
parser.add_argument('-d', '--directory', help='directory of files to ingest')
args = parser.parse_args()

if args.directory:
    directory = args.directory
else:
    directory = input('Enter directory name: ')

# authenticate
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password,
                     verify=verify).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}


# Construct JSON to post from csv
log = []
directories = os.walk(directory, topdown=True)
for root, dirs, files in directories:
    print(len(files))
    for count, file in enumerate(files):
        if file[-4:] == 'json':
            itemLog = {}
            print(count, file)
            itemLog['file'] = file
            doRecord = json.load(open(directory+'/'+file))
            itemLog['archival_object'] = doRecord['linked_instances'][0]['ref']
            itemLog['title'] = doRecord['title']
            doRecord = json.dumps(doRecord)
            link = baseURL+'/repositories/'+repo+'/digital_objects'
            post = requests.post(link,  headers=headers, verify=verify,
                                 data=doRecord).json()
            print(post)
            itemLog['uri'] = post['uri']
            log.append(itemLog)

log = pd.DataFrame.from_dict(log)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
log.to_csv('logOfNewDO_'+dt+'.csv')

# Show script runtime
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Post complete.  Total script run time: ', '%d:%02d:%02d' % (h, m, s))
