# archivesspace-api
Python scripts used to perform various tasks with the ArchivesSpace API

###Authenticating to the API

All of these scripts require a secrets.py file in the same directory that must contain the following text:

	baseURL='[ArchivesSpace API URL]'
	user='[user name]'
	password='[password]'

###getElementsFromAgentsCorporate.py

###getElementsFromAgentsPeople.py

###getElementsFromArrayInsideArray.py

###getResources.py

###getSingleRecord.py
This GET script retrieves a single ArchivesSpace record based on the record's 'uri,' which is specified in the 'endpoint' variable on line 13.

###postNew.py
This POST script will post new records to a generic API endpoint based the record type, 'agents/people' in this example .  This script can be modified to accommodate other data types (e.g. 'repositories/[repo ID]/resources' or 'agents/corporate_entities'). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post.  

###postOverwrite.py
This POST script will overwrite existing ArchivesSpace records based the 'uri' and can be used with any ArchivesSpace record type (e.g. resource, accession, subject, agent_people, agent_corporate_entity, archival_object, etc.). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post. 

###searchArchivalObjectsByResource.py
A GET script to extract all of the archival objects associated with a particular resource. To set the resource you want to search for, adjust the 'resourceNumber' variable on line 13
