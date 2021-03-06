import json
import requests
import time
import csv


def firstLevelUpdateFromCSV(key, valueSource):
    """Update first level value from CSV."""
    uri = row['uri']
    value = row[valueSource]
    if value != '':
        asRecord = requests.get(baseURL + uri, headers=headers).json()
        asRecord[key] = value
        asRecord = json.dumps(asRecord)
        post = requests.post(baseURL + uri, headers=headers,
                             data=asRecord).json()
        print(post)
    else:
        pass


def secondLevelUpdateFromCSV(key, valueSource, firstLevel):
    """Update first level value from CSV."""
    uri = row['uri']
    value = row[valueSource]
    if value != '':
        asRecord = requests.get(baseURL + uri, headers=headers).json()
        try:
            asRecord[firstLevel][key] = value
        except ValueError:
            asRecord[firstLevel] = {}
            asRecord[firstLevel][key] = value
        asRecord = json.dumps(asRecord)
        post = requests.post(baseURL + uri, headers=headers,
                             data=asRecord).json()
        print(post)
    else:
        pass


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

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

filename = input('Enter filename (including \'.csv\'): ')
filename = 'bibNumbers.csv'

with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        secondLevelUpdateFromCSV('real_1', 'bib', 'user_defined')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
