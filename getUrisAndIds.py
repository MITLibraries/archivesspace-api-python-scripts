import requests
import csv

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

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

recordType = input('Enter record type, \'resources\' or \'accessions\': ')

endpoint = '/repositories/' + repository + '/' + recordType + '?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f = csv.writer(open(recordType + 'UrisAndIds.csv', 'w'))
f.writerow(['ConCatID'] + ['id_0'] + ['id_1'] + ['id_2'] + ['id_3'] + ['id'])

for id in ids:
    print(id)
    endpoint = '/repositories/' + repository + '/' + recordType + '/' + str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    try:
        id_0 = output['id_0']
    except ValueError:
        id_0 = ''
    try:
        id_1 = '.' + output['id_1']
    except ValueError:
        id_1 = ''
    try:
        id_2 = '.' + output['id_2']
    except ValueError:
        id_2 = ''
    try:
        id_3 = '.' + output['id_3']
    except ValueError:
        id_3 = ''
    ConCatID = id_0 + id_1 + id_2 + id_3
    f.writerow([ConCatID] + [id_0] + [id_1[1:]] + [id_2[1:]] + [id_3[1:]]
               + [endpoint])
