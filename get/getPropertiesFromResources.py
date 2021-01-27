import json
import requests
import secrets
import time
import csv

secretsVersion = input('To edit production server, enter secrets file name: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Development')
else:
    print('Editing Development')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL+'/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}

endpoint = '/repositories/'+repository+'/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f = csv.writer(open('resourceProperties.csv', 'w'))
f.writerow(['title']+['uri']+['bibnum']+['type']+['value'])

total = len(ids)
for id in ids:
    print('id', id, total, 'records remaining')
    total = total - 1
    endpoint = '/repositories/'+repository+'/resources/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()

    title = output['title']
    uri = output['uri']
    try:
        bibnum = output['user_defined']['real_1']
    except:
        bibnum = ''
    try:
        agents = output['linked_agents']
        for agent in agents:
            agentUri = agent['ref']
            agentOutput = requests.get(baseURL + agentUri, headers=headers).json()
            agentName = agentOutput['title']
            f.writerow([title]+[uri]+[bibnum]+['name']+[agentName])
    except:
        pass
    try:
        subjects = output['subjects']
        for subject in subjects:
            subjectUri = subject['ref']
            subjectOutput = requests.get(baseURL + subjectUri, headers=headers).json()
            subjectName = subjectOutput['title']
            f.writerow([title]+[uri]+[bibnum]+['subject']+[subjectName])
    except:
        pass
    for note in output['notes']:
        abstract = ''
        scopecontent = ''
        acqinfo = ''
        custodhist = ''
        bioghist = ''
        accessrestrict = ''
        relatedmaterial = ''
        try:
            if note['type'] == 'abstract':
                abstract = note['content'][0]

                f.writerow([title]+[uri]+[bibnum]+['abstract']+[abstract])
            if note['type'] == 'scopecontent':
                scopecontentSubnotes = note['subnotes']
                for subnote in scopecontentSubnotes:
                    scopecontent = scopecontent + subnote['content'] + ' '
                f.writerow([title]+[uri]+[bibnum]+['scopecontent']+[scopecontent])
            if note['type'] == 'acqinfo':
                acqinfoSubnotes = note['subnotes']
                for subnote in acqinfoSubnotes:
                    acqinfo = acqinfo + subnote['content'] + ' '
                f.writerow([title]+[uri]+[bibnum]+['acqinfo']+[acqinfo])
            if note['type'] == 'custodhist':
                custodhistSubnotes = note['subnotes']
                for subnote in custodhistSubnotes:
                    custodhist = custodhist + subnote['content'] + ' '
                f.writerow([title]+[uri]+[bibnum]+['custodhist']+[custodhist])
            if note['type'] == 'bioghist':
                bioghistSubnotes = note['subnotes']
                for subnote in bioghistSubnotes:
                    bioghist = bioghist + subnote['content'] + ' '
                f.writerow([title]+[uri]+[bibnum]+['bioghist']+[bioghist])
            if note['type'] == 'accessrestrict':
                accessrestrictSubnotes = note['subnotes']
                for subnote in accessrestrictSubnotes:
                    accessrestrict = accessrestrict + subnote['content'] + ' '
                f.writerow([title]+[uri]+[bibnum]+['accessrestrict']+[accessrestrict])
            if note['type'] == 'relatedmaterial':
                relatedmaterialSubnotes = note['subnotes']
                for subnote in relatedmaterialSubnotes:
                    relatedmaterial = relatedmaterial + subnote['content'] + ' '
                f.writerow([title]+[uri]+[bibnum]+['relatedmaterial']+[relatedmaterial])
        except:
            f.writerow([title]+[uri]+[bibnum]+['']+[custodhist])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
