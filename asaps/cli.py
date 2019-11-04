import time

from asnake.client import ASnakeClient
import click

from asaps import models


@click.command()
@click.option('--url', envvar='ARCHIVESSPACE_URL')
@click.option('-u', '--username', prompt='Enter username',
              help='The username for authentication.')
@click.option('-p', '--password', prompt='Enter password',
              hide_input=True, envvar='DOCKER_PASS',
              help='The password for authentication.')
@click.option('-d', '--dry_run', prompt='Dry run?', default=True,
              help='Perform dry run that does not modify any records.')
def main(url, username, password, dry_run):
    client = ASnakeClient(baseurl=url, username=username,
                          password=password)
    as_ops = models.AsOperations(client)
    start_time = time.time()
    rec_type = 'resource'
    note_type = 'acqinfo'

    corr_dict = {'Institute Archives and Special Collections':
                 'Department of Distinctive Collections'}
    # corr_dict = {'the Institute Archives': 'Distinctive Collections'}
    # corr_dict = {'Institute Archives': 'Distinctive Collections'}
    # corr_dict = {'Distinctive Collections': 'Distinctive Collections (formerly the Institute Archives and Special Collections)'}
    # corr_dict = {'formerly the Department of Distinctive Collections': 'formerly Institute Archives and Special Collections'}

    skipped_resources = ['/repositories/2/resources/535',
                         '/repositories/2/resources/41',
                         '/repositories/2/resources/111',
                         '/repositories/2/resources/367',
                         '/repositories/2/resources/231',
                         '/repositories/2/resources/561',
                         '/repositories/2/resources/563',
                         '/repositories/2/resources/103']
    skipped_aos = []
    for uri in skipped_resources:
        aolist = as_ops.get_aos_for_resource(uri)
        skipped_aos.append(aolist)
    skipped_uris = skipped_resources + skipped_aos

    for old, new in corr_dict.items():
        for uri in as_ops.search(old, '2', rec_type, note_type):
            if uri not in skipped_uris:
                rec_obj = as_ops.get_record(uri)
                notes = models.filter_note_type(rec_obj, note_type)
                for note in notes:
                    for subnote in note.get('subnotes', []):
                        subnote['content'] = subnote['content'].replace(old,
                                                                        new)
                if rec_obj.modified is True:
                    as_ops.save_record(rec_obj, dry_run)
            else:
                print(uri, ' skipped')
    models.elapsed_time(start_time, 'Total runtime:')
    models.create_csv_from_log()


if __name__ == '__main__':
    main()
