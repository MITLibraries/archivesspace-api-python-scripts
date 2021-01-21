import csv
import os
import time

filePath = input('Enter file path (C:/Test/): ')

startTime = time.time()
f = csv.writer(open('fileListing.csv', 'w'))
f.writerow(['file'] + ['newFile'])
directories = os.walk(filePath, topdown=True)
for root, dirs, files in directories:
    for file in files:
        refID = file[18:-4]
        f.writerow([file] + [refID])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
