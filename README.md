Python scripts used to perform various tasks with the ArchivesSpace API

## Authenticating to the API

All of these scripts require a secrets.py file in the same directory that must contain the following text:

	baseURL='[ArchivesSpace API URL]'
	user='[user name]'
	password='[password]'
	repository='[repository]'

This secrets.py file will be ignored according to the repository's .gitignore file so that ArchivesSpace login details will not be inadvertently exposed through GitHub.

If you are using both a development server and a production server, you can create a separate secrets.py file with a different name (e.g. secretsProd.py) and containing the production server information. When running each of these scripts, you will be prompted to enter the file name (e.g 'secretsProd' without '.py') of an alternate secrets file. If you skip the prompt or incorrectly type the file name, the scripts will default to the information in the secrets.py file. This ensures that you will only access the production server if you really intend to.

## Scripts

#### [addBibNumbersAndPost.py](/addBibNumbersAndPost.py)
Based on a specified CSV file with URIs and bib numbers, posts the specified bib number to the ['user_defined]['real_1'] field for record specified by the URI.

#### [dateCheck.py](/dateCheck.py)
Retrieves 'begin,' 'end,' 'expression,' and 'date_type' for all dates associated with all resources in a repository

#### [eadToCsv.py](/eadToCsv.py)
Based on a specified file name and a specified file path, extracts selected elements from an EAD XML file and prints them to a CSV file.

#### [getAccessionUDFs.py](/getAccessionUDFs.py)
Retrieves all of the user-defined fields from all of the accessions in the specified repository.

#### [getAccessions.py](/getAccessions.py)
Retrieves all of the accessions from a particular repository into a JSON file.

#### [getAllArchivalObjectTitles.py](/getAllArchivalObjectTitles.py)
Retrieves titles from all archival objects in a repository. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArchivalObjectCountByResource.py](/getArchivalObjectCountByResource.py)
Retrieves a count of archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArchivalObjectsByResource.py](/getArchivalObjectsByResource.py)
Extracts all of the archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArchivalObjectRefIdsForResource.py](/getArchivalObjectRefIdsForResource.py)
Extracts the title, URI, ref_id, date expression, and level for all archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArrayPropertiesFromAgentsPeopleCSV.py](/getArrayPropertiesFromAgentsPeopleCSV.py)
Retrieves specific properties, including proprerties that have arrays as values, from the JSON of ArchivesSpace agent_people records. In this example, the 'dates_of existence' property contains an array that must be iterated over. This requires a second level of iteration with 'for j in range (...)' on line 20, which is in addition to the iteration function 'for i in range (...)' on line 19, which was also found in the getPropertiesFromAgentsPeopleCSV.py script. As with the previous script, it also writes the properties' values into a CSV file which is specified in variable 'f' on line 17.

#### [getPropertiesFromAgentsPeopleCSV.py](/getPropertiesFromAgentsPeopleCSV.py)
Retrieves specific properties from the JSON of ArchivesSpace agent_people records into a CSV file which is specified in variable 'f' on line 17. In this example, the script retrieves the 'uri,' 'sort_name,' 'authority_id,' and 'names' properties from the JSON records by iterating through the JSON records with the function 'for i in range (...)' on line 19. The f.writerow(....) function on line 20 specifies which properties are retrieved from the JSON and the f.writerow(....) on line 18 specifies header row of the CSV file.  

#### [getPropertiesFromResources.py](/getPropertiesFromResources.py)
Extracts select properties from all resources in the repository.

#### [getPropertiesFromSingleResource.py](/getPropertiesFromSingleResource.py)
Based on user input, extracts select properties from the specified resource.

#### [getResources.py](/getResources.py)
Retrieves all of the resources from a particular repository into a JSON file which is specified in variable 'f' on line 16. This GET script can be adapted to other record types by editing the 'endpoint' variable on line 13 (e.g. 'repositories/[repo ID]/accessions' or 'agents/corporate_entities').

#### [getSingleRecord.py](/getSingleRecord.py)
Based on user input, retrieves a single ArchivesSpace record based on the specified record's 'uri.'

#### [getTopContainerCountByResource.py](/getTopContainerCountByResource.py)
Retrieves a count of top containers associated with archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getTopContainerCountByResourceNoAOs.py](/getTopContainerCountByResourceNoAOs.py)
Retrieves a count of top containers directly associated (not through an archival object) with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getTopContainers.py](/getTopContainers.py)
Retrieves all of the top containers from a particular repository into a JSON file.

#### [getUrisAndIds.py](getUrisAndIds.py)
For the specified record type, retrieves URI and the 'id_0,' 'id_1,' 'id_2,' 'id_3,' and a concatenated version of all the 'id' fields.

#### [modifyDigitalObjectUrls.py](/modifyDigitalObjectUrls.py)
Based on user input, replaces a string in the URLs in both the 'Identifier' and 'File URI' fields for digital objects across the repository.

#### [postContainersFromCSV.py](/postContainersFromCSV.py)
Creates instances (consisting of top_containers) from a separate CSV file. The CSV file should have two columns, indicator and barcode. The directory where this file is stored must match the directory in the filePath variable. The script will prompt you first for the exact name of the CSV file, and then for the exact resource or accession to attach the containers to.

#### [postContainerLinksToRecords.py](/postContainerLinksToRecords.py)
Based on user input, posts containers to a specified record based on a specified CSV file.

#### [postContainerLinksToRecordsFromCSV.py](/postContainerLinksToRecordsFromCSV.py)
Based on user input, posts containers to a specified record based on a specified CSV file of top container and resource URIs.

#### [postCorporateAgentsFromCSV.py](/postCorporateAgentsFromCSV.py)
Based on user input, posts corporate agents based on a specified CSV file.

#### [postFamilyAgentsFromCSV.py](/postFamilyAgentsFromCSV.py)
Based on user input, posts family agents based on a specified CSV file.

#### [postNew.py](/postNew.py)
Posts new records to a generic API endpoint based the record type, 'agents/people' in this example. This script can be modified to accommodate other data types (e.g. 'repositories/[repo ID]/resources' or 'agents/corporate_entities'). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post.  

#### [postOverwrite.py](/postOverwrite.py)
Overwrites existing ArchivesSpace records based the 'uri' and can be used with any ArchivesSpace record type (e.g. resource, accession, subject, agent_people, agent_corporate_entity, archival_object, etc.). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post.

#### [postPeopleAgentsFromCSV.py](/postPeopleAgentsFromCSV.py)
Based on user input, posts people agents based on a specified CSV file.

#### [postRightsStatementsToRecords.py](/postRightsStatementsToRecords.py)
Posts rights statements to records based on various rights scenarios.

#### [postSubjectsFromCSV.py](/postSubjectsFromCSV.py)
Based on user input, posts subjects based on a specified CSV file.

#### [resourcesWithBibNum.py](/resourcesWithBibNum.py)
Extracts URIs of resources with bib numbers in the user-defined 'real_1' field.

#### [resourcesWithNoBibNum.py](/resourcesWithNoBibNum.py)
Prints the URIs to a CSV file of all resources in a repository without a bib number stored in the ['user_defined']['real_1'] field.

#### [searchForUnassociatedContainers.py](/searchForUnassociatedContainers.py)
Prints the URIs to a CSV file of all top containers that are not associated with a resource or archival object.

#### [transferAoDatesToDos.py](/transferAoDatesToDos.py)
Transfers the date from an archival object to any attached digital objects.

#### [unpublishArchivalObjectsByResource.py](/unpublishArchivalObjectsByResource.py)
Unpublishes all archival objects associated with the specified resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [updateResourceWithAgentOrSubjectLinks.py](/updateResourceWithAgentOrSubjectLinks.py)
Based on user input, posts agent or subject links to resources based on a specified CSV file.

#### [updateResourceWithCSV.py](/updateResourceWithCSV.py)
Based on user input, updates first level (['title']) and second level (['user_defined']['real_1']) elements for resources based on a specified CSV file.
