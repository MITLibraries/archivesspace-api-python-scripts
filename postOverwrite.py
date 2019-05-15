import json
import requests
import csv
import time
import argparse
from datetime import datetime

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
    print('Editing Development')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='the JSON file of records to post \
(including ".json"). optional - if not provided, the script will ask for \
input')
args = parser.parse_args()

if args.file:
    file = args.file
else:
    file = input('Enter the JSON file of records to post \
    (including ".json"): ')

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

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('postOverwrite' + date + '.csv', 'w'))
f.writerow(['uri'] + ['post'])

records = json.load(open(file))
for i in range(0, len(records)):
    record = json.dumps(records[i])
    uri = records[i]['uri']
    post = requests.post(baseURL + uri, headers=headers, data=record).json()
    post = json.dumps(post)
    print(post)
    f.writerow([uri] + [post])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
