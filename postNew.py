import json
import requests
import secrets
import time
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='the JSON file of records to post (including ".json"). optional - if not provided, the script will ask for input')
parser.add_argument('-e', '--endpoint', help='the endpoint for the type of records being posted (e.g "resources" or "agents/people"). optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.file:
    file = args.file
else:
    file = raw_input('Enter the JSON file of records to post (including ".json"): ')
if args.endpoint:
    endpoint = args.endpoint
else:
    endpoint = raw_input('Enter the endpoint for the type of records being posted (e.g "resources" or "agents/people"): ')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

f=csv.writer(open('postNew'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['post'])

records = json.load(open(file))
for i in range (0, len (records)):
    record = json.dumps(records[i])
    post = requests.post(baseURL + '/' + endpoint, headers=headers, data=record).json()
    post = json.dumps(post)
    print post
    f.writerow([post])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
