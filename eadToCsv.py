import csv
from bs4 import BeautifulSoup



def extractValuesFromComponentLevel (componentLevel):
        level = componentLevel.name
        componentLevelLabel = componentLevel['level']
        unittitle = componentLevel.find('did').find('unittitle').text.replace('\n','').encode('utf-8')
        try:
            unitdate = componentLevel.find('did').find('unitdate').text.encode('utf-8')
        except:
            unitdate = ''
        try:
            scopecontentElement = componentLevel.find('scopecontent').find_all('p')
            scopecontent = ''
            for paragraph in scopecontentElement:
                paragraphText = paragraph.text.replace('\n','').replace('              ',' ').replace('            ',' ').encode('utf-8')
                scopecontent = scopecontent + paragraphText
        except:
            scopecontent = ''
        try:
            container1 = componentLevel.find('did').find_all('container')[0].text.encode('utf-8')
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
            container2 = componentLevel.find('did').find_all('container')[1].text.encode('utf-8')
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
        global sortOrder
        sortOrder += 1
        f.writerow([sortOrder]+[level]+[componentLevelLabel]+[unittitle]+[unitdate]+[scopecontent]+[containerType1]+[container1]+[containerId1]+[containerType2]+[container2]+[containerId2])

filepath =  raw_input('Enter file path: ')
fileName = raw_input('Enter file name: ')
xml = open(filepath+fileName)

f=csv.writer(open(filepath+'eadFields.csv', 'wb'))
f.writerow(['sortOrder']+['<co?>']+['<co?> level']+['<unittitle>']+['<unitdate>']+['<scopecontent>']+['containerType1']+['container1']+['containerId1']+['containerType2']+['container2']+['containerId2'])
upperComponentLevels = BeautifulSoup(xml, 'lxml').find('dsc').find_all('c01')
sortOrder = 0
for upperComponentLevel in upperComponentLevels:
    componentLevelLabel = upperComponentLevel['level']
    unittitle = upperComponentLevel.find('did').find('unittitle').text.encode('utf-8')
    try:
        scopecontentElement = upperComponentLevel.find('scopecontent').find_all('p')
        scopecontent = ''
        for paragraph in scopecontentElement:
            paragraphText = paragraph.text.replace('\\n','').replace('              ',' ').replace('            ',' ').encode('utf-8')
            scopecontent = scopecontent + paragraphText
    except:
        scopecontent = ''
    sortOrder += 1
    f.writerow([sortOrder]+['c01']+[componentLevelLabel]+[unittitle]+['']+[scopecontent]+['']+['']+['']+['']+['']+[''])

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
