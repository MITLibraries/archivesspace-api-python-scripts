import pandas as pd
import json
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='filename to retreive')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter file name as filename.json: ')

with open(filename) as f:
    data = json.load(f)
    series = data['children']
    object = {}
    for child in series:
        for k, v in child.items():
            if k == 'id':
                if v == 151002:
                    object.update(child)
    children = object.get('children')
    print(children)


df_1 = pd.DataFrame.from_dict(children)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df_1.to_csv(path_or_buf='calcuateChildren_'+dt+'.csv', index=False)
