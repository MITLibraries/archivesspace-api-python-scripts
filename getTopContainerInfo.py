import requests
import secrets
import pandas as pd
import argparse
from datetime import datetime

secretsVersion = input('To edit production server, enter secrets file name: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter file name as filename.csv: ')

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

df_1 = pd.read_csv(filename)
container = df_1.top_container.dropna()
itemList = container.unique()
itemList = list(itemList)
print(itemList)


def collectValue(dictionary, property):
    if dictionary:
        value = dictionary.get(property)
        if value:
            tiny_dict[property] = value


auth = requests.post(baseURL+'/users/'+user+'/login?password='+password).json()
session = auth['session']
print(session)
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}

all_items = []
for count, item in enumerate(itemList):
    tiny_dict = {}
    print(baseURL+item)
    print(count)
    output = requests.get(baseURL+item, headers=headers).json()
    collectValue(output, 'barcode')
    collectValue(output, 'type')
    collectValue(output, 'indicator')
    collectValue(output, 'display_string')
    collectValue(output, 'uri')
    all_items.append(tiny_dict)


df = pd.DataFrame.from_dict(all_items)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='top_containers_'+dt+'.csv', index=False)
