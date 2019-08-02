import csv
import lxml
from bs4 import BeautifulSoup


def extractValuesFromcmpntLvl(cmpntLvl):
    """Extract value from the specified component level of the record."""
    level = cmpntLvl.name
    cmpntLvlLabel = cmpntLvl['level']
    unittitle = cmpntLvl.find('did').find('unittitle').text
    unittitle = unittitle.replace('\n', '')
    controlAccess = []
    originationList = []
    try:
        physdesc = cmpntLvl.find('did').find('physdesc').text
        physdesc = physdesc.replace('\n', '')
    except:
        physdesc = ''

    try:
        unitdate = cmpntLvl.find('did').find('unitdate')
        dateExpression = unitdate.text.replace('\n', '')
        try:
            dateType = unitdate['type']
        except:
            dateType = ''
        try:
            dateNormal = unitdate['normal']
            beginDate = dateNormal[:dateNormal.index('/')]
            endDate = dateNormal[dateNormal.index('/') + 1:]
        except:
            beginDate = ''
            endDate = ''
    except:
        dateExpression = ''
        dateType = ''
        beginDate = ''
        endDate = ''
    try:
        scopecontentElement = cmpntLvl.find('scopecontent')
        scopecontentElement = scopecontentElement.find_all('p')
        scopecontent = ''
        for paragraph in scopecontentElement:
            paragraphText = paragraph.text.replace('\n', '')
            scopecontent = scopecontent + paragraphText
    except:
        scopecontent = ''
    try:
        subjects = cmpntLvl.find('controlaccess').find_all()
        for subject in subjects:
            controlAccess.append(subject.text)
    except:
        subjects = ''
    try:
        container1 = cmpntLvl.find('did')
        container1 = container1.find_all('container')[0].text
    except:
        container1 = ''
    try:
        containerId1 = cmpntLvl.find('did')
        containerId1 = containerId1.find_all('container')[0]['id']
    except:
        containerId1 = ''
    try:
        containerType1 = cmpntLvl.find('did')
        containerType1 = containerType1.find_all('container')[0]['label']
    except:
        containerType1 = ''
    try:
        container2 = cmpntLvl.find('did')
        container2 = container2.find_all('container')[1].text
    except:
        container2 = ''
    try:
        containerId2 = cmpntLvl.find('did')
        containerId2 = containerId2.find_all('container')[1]['id']
    except:
        containerId2 = ''
    try:
        containerType2 = cmpntLvl.find('did')
        containerType2 = containerType2.find_all('container')[1]['label']
    except:
        containerType2 = ''
    try:
        originations = cmpntLvl.find('did').find_all('origination')
        for origination in originations:
            if origination.find()['role'] == 'spn':
                originationList.append(origination.text)
    except:
        originationList = ''
    global sortOrder
    sortOrder += 1
    f.writerow([sortOrder] + [level] + [cmpntLvlLabel]
               + [containerType1] + [container1] + [containerType2]
               + [container2] + [unittitle] + [physdesc] + [dateExpression]
               + [dateType] + [beginDate] + [endDate] + [scopecontent]
               + [controlAccess] + [originationList] + [containerId1]
               + [containerId2])


filepath = ''
fileName = 'MS.0500_20190802_142211_UTC__ead.xml'
xml = open(filepath + fileName)

f = csv.writer(open(filepath + 'eadFields.csv', 'w'))
f.writerow(['sortOrder'] + ['hierarchy'] + ['level'] + ['containerType1']
           + ['container1'] + ['containerType2'] + ['container2']
           + ['unittitle'] + ['physdesc'] + ['dateexpression'] + ['datetype']
           + ['begindate'] + ['enddate'] + ['scopecontent'] + ['controlAccess']
           + ['origination'] + ['containerId1'] + ['containerId2'])
uppercmpntLvls = BeautifulSoup(xml, 'lxml').find('dsc').find_all('c01')
sortOrder = 0
for uppercmpntLvl in uppercmpntLvls:
    cmpntLvlLabel = uppercmpntLvl['level']
    unittitle = uppercmpntLvl.find('did').find('unittitle')
    unittitle = unittitle.text.replace('\n', '')
    try:
        physdesc = uppercmpntLvl.find('did').find('physdesc').text
        physdesc = physdesc.replace('\n', '')
    except:
        physdesc = ''
    try:
        unitdate = uppercmpntLvl.find('did').find('unitdate')
        dateExpression = unitdate.text.replace('\n', '')
        try:
            dateType = unitdate['type']
        except:
            dateType = ''
        try:
            dateNormal = unitdate['normal']
            beginDate = dateNormal[:dateNormal.index('/')]
            endDate = dateNormal[dateNormal.index('/') + 1:]
        except:
            beginDate = ''
            endDate = ''
    except:
        dateExpression = ''
        dateType = ''
        beginDate = ''
        endDate = ''
    try:
        scopecontentElement = uppercmpntLvl.find('scopecontent')
        scopecontentElement = scopecontentElement.find_all('p')
        scopecontent = ''
        for paragraph in scopecontentElement:
            paragraphText = paragraph.text.replace('\\n', '')
            scopecontent = scopecontent + paragraphText
    except:
        scopecontent = ''
    sortOrder += 1
    f.writerow([sortOrder] + ['c01'] + [cmpntLvlLabel] + [''] + ['']
               + [''] + [''] + [unittitle] + [physdesc] + [dateExpression]
               + [dateType] + [beginDate] + [endDate] + [scopecontent] + ['']
               + [''] + [''] + [''])

    cmpntLvlArray = uppercmpntLvl.find_all('c02')
    for cmpntLvl in cmpntLvlArray:
        extractValuesFromcmpntLvl(cmpntLvl)
        cmpntLvlArray = cmpntLvl.find_all('c03')
        for cmpntLvl in cmpntLvlArray:
            extractValuesFromcmpntLvl(cmpntLvl)
            cmpntLvlArray = cmpntLvl.find_all('c04')
            for cmpntLvl in cmpntLvlArray:
                extractValuesFromcmpntLvl(cmpntLvl)
                cmpntLvlArray = cmpntLvl.find_all('c05')
                for cmpntLvl in cmpntLvlArray:
                    extractValuesFromcmpntLvl(cmpntLvl)
                    cmpntLvlArray = cmpntLvl.find_all('c06')
                    for cmpntLvl in cmpntLvlArray:
                        extractValuesFromcmpntLvl(cmpntLvl)
                        cmpntLvlArray = cmpntLvl.find_all('c07')
                        for cmpntLvl in cmpntLvlArray:
                            extractValuesFromcmpntLvl(cmpntLvl)
                            cmpntLvlArray = cmpntLvl.find_all('c08')
                            for cmpntLvl in cmpntLvlArray:
                                extractValuesFromcmpntLvl(cmpntLvl)
                                cmpntLvlArray = cmpntLvl.find_all('c09')
                                for cmpntLvl in cmpntLvlArray:
                                    extractValuesFromcmpntLvl(cmpntLvl)
                                    cmpntLvlArray = cmpntLvl.find_all('c10')
                                    for cmpntLvl in cmpntLvlArray:
                                        extractValuesFromcmpntLvl(cmpntLvl)
