Python scripts used to perform various tasks with the ArchivesSpace API

## Authenticating to the API

All of these scripts require a secrets.py file in the same directory that must contain the following text:

	baseURL='[ArchivesSpace API URL]'
	user='[user name]'
	password='[password]'

## Scripts

#### [addBibNumbersAndPost.py](/addBibNumbersAndPost.py)
Based on a specified CSV file with URIs and bib numbers, this script posts the specified bib number to the ['user_defined]['real_1'] field for record specified by the URI.

#### [dateCheck.py](/dateCheck.py)
Retrieves 'begin,' 'end,' 'expression,' and 'date_type' for all dates associated with all resources in a repository

#### [eadToCsv.py](/eadToCsv.py)
Based on a specified file name and a specified file path, this script extracts selected elements from an EAD XML file and prints them to a CSV file.

#### [getAccessionUDFs.py](/getAccessionUDFs.py)
This GET script retrieves all of the user-defined fields from all of the accessions in the specified repository.

#### [getAccessions.py](/getAccessions.py)
This GET script retrieves all of the accessions from a particular repository into a JSON file.

#### [getAllArchivalObjectTitles.py](/getAllArchivalObjectTitles.py)
Retrieves titles from all archival objects in a repository. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArchivalObjectCountByResource.py](/getArchivalObjectCountByResource.py)
Retrieves a count of archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArchivalObjectsByResource.py](/getArchivalObjectsByResource.py)
A GET script to extract all of the archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArrayPropertiesFromAgentsPeopleCSV.py](/getArrayPropertiesFromAgentsPeopleCSV.py)
This GET script retrieves specific properties, including proprerties that have arrays as values, from the JSON of ArchivesSpace agent_people records. In this example, the 'dates_of existence' property contains an array that must be iterated over. This requires a second level of iteration with 'for j in range (...)' on line 20, which is in addition to the iteration function 'for i in range (...)' on line 19, which was also found in the getPropertiesFromAgentsPeopleCSV.py script. As with the previous script, it also writes the properties' values into a CSV file which is specified in variable 'f' on line 17.

#### [getPropertiesFromAgentsPeopleCSV.py](/getPropertiesFromAgentsPeopleCSV.py)
This GET script retrieves specific properties from the JSON of ArchivesSpace agent_people records into a CSV file which is specified in variable 'f' on line 17. In this example, the script retrieves the 'uri,' 'sort_name,' 'authority_id,' and 'names' properties from the JSON records by iterating through the JSON records with the function 'for i in range (...)' on line 19. The f.writerow(....) function on line 20 specifies which properties are retrieved from the JSON and the f.writerow(....) on line 18 specifies header row of the CSV file.  

#### [getResources.py](/getResources.py)
This GET scripts retrieves all of the resources from a particular repository into a JSON file which is specified in variable 'f' on line 16. This GET script can be adapted to other record types by editing the 'endpoint' variable on line 13 (e.g. 'repositories/[repo ID]/accessions' or 'agents/corporate_entities').

#### [getSingleRecord.py](/getSingleRecord.py)
This GET script retrieves a single ArchivesSpace record based on the record's 'uri,' which is specified in the 'endpoint' variable on line 13.

#### [getTopContainerCountByResource.py](/getTopContainerCountByResource.py)
Retrieves a count of top containers associated with archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getTopContainerCountByResourceNoAOs.py](/getTopContainerCountByResourceNoAOs.py)
Retrieves a count of top containers directly associated (not through an archival object) with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getTopContainers.py](/getTopContainers.py)
This GET script retrieves all of the top containers from a particular repository into a JSON file.

#### [getUrisAndIds.py](getUrisAndIds.py)
For the specified record type, this script retrieves URI and the 'id_0,' 'id_1,' 'id_2,' 'id_3,' and a concatenated version of all the 'id' fields.

#### [postContainersFromCSV.py](/postContainersFromCSV.py)
This script works to create instances (consisting of top_containers) from a separate CSV file. The CSV file should have two columns, indicator and barcode. The directory where this file is stored must match the directory in the filePath variable. The script will prompt you first for the exact name of the CSV file, and then for the exact resource or accession to attach the containers to.

#### [postNew.py](/postNew.py)
This POST script will post new records to a generic API endpoint based the record type, 'agents/people' in this example. This script can be modified to accommodate other data types (e.g. 'repositories/[repo ID]/resources' or 'agents/corporate_entities'). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post.  

#### [postOverwrite.py](/postOverwrite.py)
This POST script will overwrite existing ArchivesSpace records based the 'uri' and can be used with any ArchivesSpace record type (e.g. resource, accession, subject, agent_people, agent_corporate_entity, archival_object, etc.). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post.

#### [resourcesWithNoBibNum.py](/resourcesWithNoBibNum.py)

#### [searchForUnassociatedContainers.py](/searchForUnassociatedContainers.py)

#### [unpublishArchivalObjectsByResource.py](/unpublishArchivalObjectsByResource.py)

#### [updateFindingAidData.py](/updateFindingAidData.py)

#### [updateResourceWithCSV.py](/updateResourceWithCSV.py)
