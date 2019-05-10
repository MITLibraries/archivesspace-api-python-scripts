import json
import requests
import secrets
import time
import csv
import argparse


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
parser.add_argument('-i', '--id', help='resourceID of the object to retreive. optional - if not provided, the script will ask for input')

args = parser.parse_args()

if args.id:
    resourceID = args.id
else:
    resourceID = input('Enter resource ID: ')

startTime = time.time()

def findKey(d, key):
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j

# def createMetadataElementCSV (key, valueSource, language):

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}


endpoint = '/repositories/'+repository+'/resources/'+resourceID+'/tree'
print(endpoint)
output = requests.get(baseURL + endpoint, headers=headers).json()

archivalObjects = []
for value in findKey(output, 'record_uri'):
    archivalObjects.append(value)

collection = ''
series = ''
subseries = ''
file = ''

list = []
for archivalObject in archivalObjects:
    output = requests.get(baseURL + archivalObject, headers=headers).json()
    title = output['title']
    uri = output['uri']
    level = output['level']
    if level == 'collection':
        continue
    if level == 'series':
        series = output['title']
    if level == 'subseries':
        subseries = output['title']
    if level == 'file':
        file = output['title']
    print(title, uri, level, series, subseries, file)
    # try:
    #     ref_id = output['ref_id']
    # except:
    #     ref_id = ''
    # try:
    #     parent = output['parent']['ref']
    # except:
    #     parent = ''
    # for date in output['dates']:
    #     try:
    #         dateExpression = date['expression']
    #     except:
    #         dateExpression = ''
    #     try:
    #         dateBegin = date['begin']
    #     except:
    #         dateBegin = ''
    # list.append({'title': title, 'uri': uri, 'parent': parent})

# for item in list:
#     try:
#         parent = item['parent']
#         for item2 in list:
#              if parent == item2['uri']:
#                  try:
#                      grandparent = item2['parent']
#                      parentTitle = item2['title']
#                      item.update({'grandparent':grandparent, 'parentTitle': parentTitle})
#                      print(item)
#                  except:
#                      item.update({'grandparent':'none'})
#     except:
#         pass
#
# for item in list:
#     try:
#         grandparent = item['grandparent']
#         for item2 in list:
#              if grandparent  == item2['uri']:
#                  try:
#                      greatgrandparent = item2['parent']
#                      grandparentTitle = item2['title']
#                      item.update({'greatgrandparent':greatgrandparent, 'grandparentTitle': grandparentTitle})
#                      print(item)
#                  except:
#                      pass
#     except:
#         pass
#
# with open('resourceTree'+resourceID+'.csv', 'w') as resource:
#     keys = ['title','uri','ref_id','dateExpression','dataBegin','level','parent','parentTitle','grandparent','grandparentTitle', 'greatgrandparent']
#     f = csv.DictWriter(resource, keys)
#     f.writeheader()
#     f.writerows(list)



def findHierarchy(x, y, z):
    for item in list:
        try:
            parent = item[x]
            for item2 in list:
                 if parent == item2['uri']:
                     try:
                         grandparent = item2['firstGen']
                         parentTitle = item2['title']
                         item.update({y: grandparent, z: parentTitle})
                         print(item)
                     except:
                         item.update({y:'none'})
        except:
            pass


findHierarchy(x='firstGen', y='secondGen', z='firstGenName')
findHierarchy(x='secondGen', y='thirdGen',z= 'secondGenName')
findHierarchy(x='thirdGen', y='fourthGen', z='thirdGenName')
findHierarchy(x='fourthGen', y='fifthGen', z='fourthGenName')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
