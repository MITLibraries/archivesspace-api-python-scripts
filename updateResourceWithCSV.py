import json
import requests
import secrets
import time
import csv

def firstLevelUpdateFromCSV (key, valueSource):
    uri = row['uri']
    value = row[valueSource]
    if value != '':
        asRecord = requests.get(baseURL+uri, headers=headers).json()
        asRecord[key] = value
        asRecord = json.dumps(asRecord)
        post = requests.post(baseURL + uri, headers=headers, data=asRecord).json()
        print(post)
    else:
        pass

def secondLevelUpdateFromCSV (key, valueSource, firstLevel):
    uri = row['uri']
    value = row[valueSource]
    if value != '':
        asRecord = requests.get(baseURL+uri, headers=headers).json()
        try:
            asRecord[firstLevel][key] = value
        except:
            asRecord[firstLevel]= {}
            asRecord[firstLevel][key] = value
        asRecord = json.dumps(asRecord)
        post = requests.post(baseURL + uri, headers=headers, data=asRecord).json()
        print(post)
    else:
        pass

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

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
