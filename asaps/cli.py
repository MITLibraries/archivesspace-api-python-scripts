import click
import models
from asnake.client import ASnakeClient


@click.command()
@click.option('--url', envvar='ARCHIVESSPACE_URL')
@click.option('-u', '--username', prompt='Enter username',
              help='The username for authentication.')
@click.option('-p', '--password', prompt='Enter password',
              hide_input=True, envvar='DOCKER_PASS',
              help='The password for authentication.')
def main(url, username, password):
    client = ASnakeClient(baseurl=url, username=username,
                          password=password)
    as_ops = models.AsOperations(client)

    # # Sample code for testing
    # csv_data = []
    rec_obj = as_ops.get_record('/repositories/2/resources/423')
    models.download_json(rec_obj)
    # rec_obj = models.filter_note_type(client, csv_data, rec_obj,
    #                                   'accessrestrict', 'replace_str', 'The',
    #                                   'barg')
    # print(rec_obj['notes'])
    # csv_row = {}
    # response = as_ops.post_record(rec_obj, csv_row, csv_data)
    # csv_row['response'] = response
    # csv_data.append(csv_row)
    # results = as_ops.search('Chomsky', '2', 'resource')
    # for result in results:
    #     print(result['uri'])


if __name__ == '__main__':
    main()
