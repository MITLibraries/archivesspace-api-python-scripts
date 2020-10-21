import requests
import secrets
import pandas as pd
import argparse
from datetime import datetime

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
parser.add_argument('-f', '--file', help='file_name to retreive')
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
itemList = df_1.record_uri.to_list()


def collectProperty(dictionary, property, name=None):
    if dictionary is not None:
        value = dictionary.get(property)
        if value is not None:
            if name:
                tiny_dict[name] = value
            else:
                tiny_dict[property] = value


auth = requests.post(baseURL+'/users/'+user+'/login?password='+password).json()
session = auth['session']
print(auth)
print(session)
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}
all_items = []
for count, item in enumerate(itemList):
    if 2000 <= count:
        tiny_dict = {}
        print(baseURL+item)
        output = requests.get(baseURL+item, headers=headers).json()
        collectProperty(output, 'uri')
        collectProperty(output, 'title')
        dates = output.get('dates')
        for date in dates:
            collectProperty(date, 'expression')
        instances = output.get('instances')
        for item in instances:
            sub_container = item.get('sub_container')
            if sub_container:
                top_container = sub_container.get('top_container')
                collectProperty(top_container, 'ref', 'container')
            digital_object = item.get('digital_object')
            collectProperty(digital_object, 'ref', 'digital')
        all_items.append(tiny_dict)


df = pd.DataFrame.from_dict(all_items)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='childRecords3_'+dt+'.csv', index=False)
