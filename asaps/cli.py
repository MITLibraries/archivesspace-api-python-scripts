import time

from asnake.client import ASnakeClient
import click

from asaps import models


@click.command()
@click.option('--url', envvar='ARCHIVESSPACE_URL')
@click.option('-u', '--username', prompt='Enter username',
              help='The username for authentication.')
@click.option('-p', '--password', prompt='Enter password',
              hide_input=True,  # envvar='DOCKER_PASS',
              help='The password for authentication.')
def main(url, username, password):
    client = ASnakeClient(baseurl=url, username=username,
                          password=password)
    as_ops = models.AsOperations(client)
    start_time = time.time()

    csv_data = []
    rec_type = 'resource'
    repo_id = '2'
    note_type = 'prefercite'
    old = 'the'
    new = 'that'
    endpoint = as_ops.create_endpoint(rec_type, repo_id)
    ids = as_ops.get_all_records(endpoint)
    print(ids)
    for id in ids:
        uri = f'{endpoint}/{id}'
        print(uri)
        rec_obj = as_ops.get_record(uri)
        rec_obj = models.filter_note_type(as_ops, csv_data,
                                          rec_obj, note_type,
                                          'find_replace_test',
                                          old, new)

    # rec_types = ['resource', 'archival_object']
    # corr_dict = {'IASC': 'DDC'}
    # # corr_dict = {'Institute Archives and Special Collections':
    # #              'Department of Distinctive Collections'}
    # # corr_dict = {'the Institute Archives': 'Distinctive Collections'}
    # # corr_dict = {'Institute Archives': 'Distinctive Collections'}
    # # corr_dict = {'IASC': 'DDC',
    # #              'Institute Archives and Special Collections':
    # #              'Department of Distinctive Collections',
    # #              'the Institute Archives': 'Distinctive Collections'}  # ,
    # #              # 'Institute Archives': 'Distinctive Collections'}
    #
    # error_uris = ['/repositories/2/resources/424',
    #               '/repositories/2/resources/1233',
    #               '/repositories/2/resources/377',
    #               '/repositories/2/resources/356',
    #               '/repositories/2/resources/228',
    #               '/repositories/2/resources/658',
    #               '/repositories/2/resources/635',
    #               '/repositories/2/resources/704',
    #               '/repositories/2/resources/202',
    #               '/repositories/2/resources/586']
    #
    # skipped_resources = ['/repositories/2/resources/535',
    #                      '/repositories/2/resources/41',
    #                      '/repositories/2/resources/111',
    #                      '/repositories/2/resources/367',
    #                      '/repositories/2/resources/231',
    #                      '/repositories/2/resources/561',
    #                      '/repositories/2/resources/563',
    #                      '/repositories/2/resources/103']
    # skipped_aos = []
    # for uri in skipped_resources:
    #     aolist = as_ops.get_aos_for_resource(uri)
    #     skipped_aos.append(aolist)
    # skipped_uris = error_uris + skipped_resources + skipped_aos
    # csv_data = []
    # note_types = ['userestrict', 'acqinfo']
    # counter = 0
    # for rec_type in rec_types:
    #     for old, new in corr_dict.items():
    #         results = as_ops.search(old, '2', rec_type)
    #         for result in results:
    #             counter += 1
    #             uri = result['uri']
    #             if uri not in skipped_uris:
    #                 for note_type in note_types:
    #                     print(old, rec_type, note_type, counter)
    #                     rec_obj = as_ops.get_record(uri)
    #                     rec_obj = models.filter_note_type(as_ops, csv_data,
    #                                                       rec_obj, note_type,
    #                                                       'find_replace_test',
    #                                                       old, new)
    #         else:
    #             print(uri, ' skipped')
    if len(csv_data) != 0:
        models.create_csv(csv_data, 'replace_str')
    else:
        print('No files updated')
    models.elapsed_time(start_time, 'Total runtime:')


if __name__ == '__main__':
    main()
