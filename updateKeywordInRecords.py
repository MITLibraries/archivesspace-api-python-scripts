import json
import requests
import secrets
import time
import csv
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
parser.add_argument('-f', '--file', help='Enter the name of the file, including the .csv')
parser.add_argument('-k', '--keyword', help='Keyword to retreive. optional - if not provided, the script will ask for input')
parser.add_argument('-r', '--replacement', help='Replacement for original keyword. optional - if not provided, the script will ask for input')
parser.add_argument('-m', '--make_changes', help= "Enter 'yes' if you want to change the records in ArchiveSpace. Else, the script will only produce a csv of expected changes.")
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter the name of the file: ')
if args.keyword:
    keyword = args.keyword
else:
    keyword = input('Enter keyword to search: ')
if args.replacement:
    replacement = args.replacement
else:
    replacement = input('Enter the replacement for the keyword: ')
if args.make_changes == 'yes':
    make_changes = 'yes'
else:
    make_changes = 'no'


startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
print('authenticated')

keywordFile = keyword.capitalize()

f=csv.writer(open('propertiesContaining'+keywordFile+'InRecordtesting.csv', 'w'))


with open(filename, encoding = 'utf-8') as changesFile:
    elements = csv.DictReader(changesFile)
    for element in elements:
        changes = 0
        endpoint = element['uri'].strip()
        print('')
        print(endpoint)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        newoutput = output
        uri = output['uri']
        def replaceString(variable, json_key):
            global newoutput
            global changes
            try:
                variable_name = variable
                variable = output[json_key]
                if keyword in variable:
                    changes = changes + 1
                    print('found '+variable_name+': '+variable)
                    f.writerow(['original']+[uri]+[variable_name]+[variable])
                    variable = variable.replace(keyword, replacement)
                    newoutput[json_key] = variable
                    new_variable = newoutput[json_key]
                    f.writerow(['replaced']+[uri]+[variable_name]+[new_variable])
                    print('replaced '+variable_name+': '+new_variable)
            except:
                pass
        def replaceString2(variable, json_key, json_key2):
            global newoutput
            global changes
            try:
                variable_name = variable
                variable = output[json_key][json_key2]
                if keyword in variable:
                    changes = changes + 1
                    print('found '+variable_name+': '+variable)
                    f.writerow(['original']+[uri]+[variable_name]+[variable])
                    variable = variable.replace(keyword, replacement)
                    newoutput[json_key][json_key2] = variable
                    new_variable = newoutput[json_key][json_key2]
                    f.writerow(['replaced']+[uri]+[variable_name]+[new_variable])
                    print('replaced '+variable_name+': '+new_variable)
            except:
                pass
        def replaceString3(variable, json_key, json_key2, integer):
            global newoutput
            global changes
            try:
                variable_name = variable
                variable = output[json_key][integer][json_key2]
                if keyword in variable:
                    changes = changes + 1
                    print('found '+variable_name+': '+variable)
                    f.writerow(['original']+[uri]+[variable_name]+[variable])
                    variable = variable.replace(keyword, replacement)
                    newoutput[json_key][integer][json_key2] = variable
                    new_variable = newoutput[json_key][integer][json_key2]
                    f.writerow(['replaced']+[uri]+[variable_name]+[new_variable])
                    print('replaced '+variable_name+': '+new_variable)
            except:
                pass
        replaceString(variable='title', json_key='title')
        replaceString(variable='finding_aid_title', json_key='finding_aid_title')
        replaceString(variable='content_description', json_key='content_description')
        replaceString(variable='condition_description', json_key='condition_description')
        replaceString(variable='inventory', json_key='inventory')
        replaceString(variable='accession_date', json_key='accession_date')
        replaceString(variable='access_restrictions_note', json_key='access_restrictions_note')
        replaceString(variable='use_restrictions_note', json_key='use_restrictions_note')
        replaceString2(variable='appraisalLegacy', json_key='user_defined', json_key2='string_4')
        replaceString2(variable='custodialHistory', json_key='user_defined', json_key2='text_1')
        replaceString2(variable='electronicRecordLog', json_key='user_defined', json_key2='text_2')
        replaceString2(variable='relatedMaterialsNote', json_key='user_defined', json_key2='text_3')
        replaceString2(variable='archiveItSeeds', json_key='user_defined',json_key2='text_4')
        replaceString2(variable='appraisal', json_key='user_defined', json_key2='text_5')
        replaceString2(variable='accessionStatus', json_key='user_defined', json_key2='enum_1')
        for x in range(0,4):
            replaceString3(variable='dates_expression', json_key='dates', json_key2='expression', integer=x)
            replaceString3(variable='dates_begin', json_key='dates', json_key2='begin', integer=x)
            replaceString3(variable='dates_end', json_key='dates', json_key2='end', integer=x)
        for x in range(10):
            try:
                note = output['notes'][x]
                for y in range(10):
                    subnote = note['subnotes'][y]['content']
                    try:
                        note_name = note['type']
                    except:
                        note_name = ''
                    if keyword in subnote:
                        changes = changes + 1
                        print('found '+note_name+': '+subnote)
                        f.writerow(['original']+[uri]+[note_name]+[subnote])
                        subnote = subnote.replace(keyword, replacement)
                        newoutput['notes'][x]['subnotes'][y]['content'] = subnote
                        new_subnote = newoutput['notes'][x]['subnotes'][y]['content']
                        f.writerow(['replaced']+[uri]+[note_name]+[new_subnote])
                        print('replaced '+note_name+': '+new_subnote)
            except:
                pass
        for x in range(3):
            try:
                note = output['notes'][x]
                for y in range(3):
                    abstract = note['content'][y]
                    if keyword in abstract:
                        changes = changes + 1
                        print('found abstract: '+abstract)
                        f.writerow(['original']+[uri]+['abstract']+[abstract])
                        abstract = abstract.replace(keyword, replacement)
                        newoutput['notes'][x]['content'][y] = abstract
                        new_abstract = newoutput['notes'][x]['content'][y]
                        f.writerow(['replaced']+[uri]+['abstract']+[new_abstract])
                        print('replaced abstract: '+new_abstract)
            except:
                pass

        if changes != 0:
            if make_changes == 'yes':
                print('Replacing {} with {} in record {}'.format(keyword, replacement, uri))
            else:
                print('Found changes to replace {} with {} in record {}. Recording in CSV.'.format(keyword, replacement, uri))
        else:
            print('Nothing to replace in record {}'.format(uri) )


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
