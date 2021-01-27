import csv
import json
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')


def addToDict(dict, key, value):
    try:
        value = row[value]
        if value:
            value = value.strip()
            dict[key] = value
    except KeyError:
        pass


with open(filename) as metadata:
    metadata = csv.DictReader(metadata)
    for row in metadata:
        json_file = {}
        date = {}
        file_version = {}
        linked_instance = {}
        json_file['jsonmodel_type'] = 'digital_object'
        json_file['is_slug_auto'] = False
        json_file['suppressed'] = False
        json_file['restrictions'] = False
        json_file['publish'] = True
        json_file['file_versions'] = []
        json_file['linked_instances'] = []
        json_file['repository'] = {"ref": "/repositories/3"}
        file_version['jsonmodel_type'] = 'file_version'
        file_version['is_representative'] = False
        file_version['publish'] = True
        addToDict(date, 'expression', 'expression')
        addToDict(date, 'begin', 'begin')
        addToDict(date, 'end', 'end')
        addToDict(date, 'date_type', 'date_type')
        addToDict(date, 'label', 'label')
        addToDict(file_version, 'file_uri', 'file_uri')
        addToDict(json_file, 'title', 'title')
        addToDict(json_file, 'digital_object_id', 'file_uri')
        addToDict(linked_instance, 'ref', 'record_uri')
        identifier = row['record_uri']
        identifier = identifier.replace('/repositories/3/archival_objects/', 'do_')
        if date:
            date['jsonmodel_type'] = 'date'
            json_file['dates'] = [date]
        if file_version:
            json_file['file_versions'] = [file_version]
        if linked_instance:
            json_file['linked_instances'] = [linked_instance]
        dt = datetime.now().strftime('%Y-%m-%d')
        c_filename = identifier+'_'+dt+'.json'
        directory = ''
        with open(directory+c_filename, 'w') as fp:
            json.dump(json_file, fp)
