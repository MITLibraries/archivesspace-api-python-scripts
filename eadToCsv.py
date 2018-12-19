import csv
from bs4 import BeautifulSoup

def extractValuesFromComponentLevel (componentLevel):
        level = componentLevel.name
        componentLevelLabel = componentLevel['level']
        unittitle = componentLevel.find('did').find('unittitle').text.replace('\n','')
        controlAccess = []
        originationList = []
        try:
            physdesc = componentLevel.find('did').find('physdesc').text.replace('\n','')
        except:
            physdesc = ''
        try:
            unitdate = componentLevel.find('did').find('unitdate')
            dateExpression = unitdate.text.replace('\n','').replace('              ',' ').replace('            ',' ')
            try:
                dateType = unitdate['type']
            except:
                dateType = ''
            try:
                dateNormal = unitdate['normal']
                beginDate = dateNormal[:dateNormal.index('/')]
                endDate = dateNormal[dateNormal.index('/')+1:]
            except:
                beginDate = ''
                endDate = ''
        except:
            dateExpression = ''
            dateType = ''
            beginDate = ''
            endDate = ''
        try:
            scopecontentElement = componentLevel.find('scopecontent').find_all('p')
            scopecontent = ''
            for paragraph in scopecontentElement:
                paragraphText = paragraph.text.replace('\n','').replace('              ',' ').replace('            ',' ')
                scopecontent = scopecontent + paragraphText
        except:
            scopecontent = ''
        try:
            subjects = componentLevel.find('controlaccess').find_all()
            for subject in subjects:
                controlAccess.append(subject.text)
        except:
            subjects = ''
        try:
            container1 = componentLevel.find('did').find_all('container')[0].text
        except:
            container1 = ''
        try:
            containerId1 = componentLevel.find('did').find_all('container')[0]['id']
        except:
            containerId1 = ''
        try:
            containerType1 = componentLevel.find('did').find_all('container')[0]['type']
        except:
            containerType1 = ''
        try:
            container2 = componentLevel.find('did').find_all('container')[1].text
        except:
            container2 = ''
        try:
            containerId2 = componentLevel.find('did').find_all('container')[1]['id']
        except:
            containerId2 = ''
        try:
            containerType2 = componentLevel.find('did').find_all('container')[1]['type']
        except:
            containerType2 = ''
        try:
            originations = componentLevel.find('did').find_all('origination')
            for origination in originations:
                if origination.find()['role'] == 'spn':
                    originationList.append(origination.text)
        except:
            originationList = ''
        global sortOrder
        sortOrder += 1
        f.writerow([sortOrder]+[level]+[componentLevelLabel]+[containerType1]+[container1]+[containerType2]+[container2]+[unittitle]+[physdesc]+[dateExpression]+[dateType]+[beginDate]+[endDate]+[scopecontent]+[controlAccess]+[originationList]+[containerId1]+[containerId2])

filepath = ''
fileName = 'Coll.004_20181012_144804_UTC__ead.xml'
xml = open(filepath+fileName)

f=csv.writer(open(filepath+'eadFields.csv', 'w'))
f.writerow(['sortOrder']+['hierarchy']+['level']+['containerType1']+['container1']+['containerType2']+['container2']+['unittitle']+['physdesc']+['dateexpression']+['datetype']+['begindate']+['enddate']+['scopecontent']+['controlAccess']+['origination']+['containerId1']+['containerId2'])
upperComponentLevels = BeautifulSoup(xml, 'lxml').find('dsc').find_all('c01')
sortOrder = 0
for upperComponentLevel in upperComponentLevels:
    componentLevelLabel = upperComponentLevel['level']
    unittitle = upperComponentLevel.find('did').find('unittitle').text.replace('\n','').replace('              ', ' ')
    try:
        unitdate = upperComponentLevel.find('did').find('unitdate')
        dateExpression = unitdate.text.replace('\n','').replace('              ',' ').replace('            ',' ')
        try:
            dateType = unitdate['type']
        except:
            dateType = ''
        try:
            dateNormal = unitdate['normal']
            beginDate = dateNormal[:dateNormal.index('/')]
            endDate = dateNormal[dateNormal.index('/')+1:]
        except:
            beginDate = ''
            endDate = ''
    except:
        dateExpression = ''
        dateType = ''
        beginDate = ''
        endDate = ''
    try:
        scopecontentElement = upperComponentLevel.find('scopecontent').find_all('p')
        scopecontent = ''
        for paragraph in scopecontentElement:
            paragraphText = paragraph.text.replace('\\n','').replace('              ',' ').replace('            ',' ')
            scopecontent = scopecontent + paragraphText
    except:
        scopecontent = ''
    sortOrder += 1
    f.writerow([sortOrder]+['c01']+[componentLevelLabel]+['']+['']+['']+['']+[unittitle]+['']+[dateExpression]+[dateType]+[beginDate]+[endDate]+[scopecontent]+['']+['']+['']+[''])

    componentLevelArray = upperComponentLevel.find_all('c02')
    for componentLevel in componentLevelArray:
        extractValuesFromComponentLevel(componentLevel)
        componentLevelArray = componentLevel.find_all('c03')
        for componentLevel in componentLevelArray:
            extractValuesFromComponentLevel(componentLevel)
            componentLevelArray = componentLevel.find_all('c04')
            for componentLevel in componentLevelArray:
                extractValuesFromComponentLevel(componentLevel)
                componentLevelArray = componentLevel.find_all('c05')
                for componentLevel in componentLevelArray:
                    extractValuesFromComponentLevel(componentLevel)
                    componentLevelArray = componentLevel.find_all('c06')
                    for componentLevel in componentLevelArray:
                        extractValuesFromComponentLevel(componentLevel)
                        componentLevelArray = componentLevel.find_all('c07')
                        for componentLevel in componentLevelArray:
                            extractValuesFromComponentLevel(componentLevel)
                            componentLevelArray = componentLevel.find_all('c08')
                            for componentLevel in componentLevelArray:
                                extractValuesFromComponentLevel(componentLevel)
                                componentLevelArray = componentLevel.find_all('c09')
                                for componentLevel in componentLevelArray:
                                    extractValuesFromComponentLevel(componentLevel)
                                    componentLevelArray = componentLevel.find_all('c10')
                                    for componentLevel in componentLevelArray:
                                        extractValuesFromComponentLevel(componentLevel)
