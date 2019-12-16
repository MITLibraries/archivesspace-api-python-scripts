# asaps

This command line application provides several ways of interacting with the [ArchivesSpace](https://github.com/archivesspace/archivesspace) API.

## Installation
Clone repo and install using [pipenv](https://github.com/pypa/pipenv):
```bash
pipenv install -e .
```

## Authentication

To authenticate, use the following parameters

Option (short) | Option (long) | Description
------ | ------ | -------
N/A | --url | The ArchivesSpace API URL (e.g. https://archivesspace.mit.edu/api), defaults to the ARCHIVESSPACE_URL environmental variable if nothing is specified
-u | --username | The username for authentication
-p | --password | The password for authentication

## Commands
### report
Generates a CSV of the specified field from the specified record type
Example usage

Option (short) | Option (long) | Description
------ | ------ | -------
-i | --repo_id | The ID of the repository to use.
-t | --rec_type | The record type to use.
-f | --field | The field to extract.

##### Example usage

`pipenv run asaps -u <username> --url <ASpace URL> find <search string> -i 2 -t resource -n acqinfo -r <replacement string> -d True`

### find
Find Enter the value to searched as an argument followed by various options to refine the query. The dry_run option defaults to `True` which will produce a CSV of the changes that would be made but no records will be modified unless the user sets the option to `False`

Option (short) | Option (long) | Description
------ | ------ | -------
-d | --dry_run | If True, performs dry run that does not modify any records.
-i | --repo_id | The ID of the repository to use.
-t | --rec_type | The record type to use.
-n | --note_type | The note type to edit.
-r | --rpl_value | The replacement value to be inserted.

##### Example usage
`pipenv run asaps -u <username> --url <ASpace URL> find <search string> -i 2 -t resource -n acqinfo -r <replacement string> -d True`
