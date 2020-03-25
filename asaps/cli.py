import csv
import datetime
import logging
import os
import time

from asnake.client import ASnakeClient
import click
import structlog

from asaps import models

logger = structlog.get_logger()


note_type_fields = ['abstract', 'accessrestrict', 'acqinfo', 'altformavail',
                    'arrangement', 'bibliography', 'bioghist', 'prefercite',
                    'processinfo' 'relatedmaterial', 'scopecontent',
                    'userestrict']
obj_field_dict = {'dates': ['begin', 'end', 'expression', 'label',
                  'date_type'],
                  'extents': ['portion', 'number', 'extent_type',
                              'container_summary',
                              'physical_details', 'dimensions']}

skipped_resources = []


@click.group()
@click.option('--url', envvar='ARCHIVESSPACE_URL')
@click.option('-u', '--username', prompt='Enter username',
              help='The username for authentication.')
@click.option('-p', '--password', prompt='Enter password',
              hide_input=True, envvar='DOCKER_PASS',
              help='The password for authentication.')
@click.pass_context
def main(ctx, url, username, password):
    ctx.obj = {}
    if os.path.isdir('logs') is False:
        os.mkdir('logs')
    dt = datetime.datetime.utcnow().isoformat(timespec='seconds')
    log_suffix = f'{dt}.log'
    structlog.configure(processors=[
                        structlog.stdlib.filter_by_level,
                        structlog.stdlib.add_log_level,
                        structlog.stdlib.PositionalArgumentsFormatter(),
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.JSONRenderer()
                        ],
                        context_class=dict,
                        logger_factory=structlog.stdlib.LoggerFactory())
    logging.basicConfig(format="%(message)s",
                        handlers=[logging.FileHandler(f'logs/log-{log_suffix}',
                                  'w')],
                        level=logging.INFO)
    logger.info('Application start')

    client = ASnakeClient(baseurl=url, username=username, password=password)
    as_ops = models.AsOperations(client)
    start_time = time.time()
    ctx.obj['as_ops'] = as_ops
    ctx.obj['start_time'] = start_time
    ctx.obj['log_suffix'] = log_suffix


@main.command()
@click.option('-i', '--repo_id', prompt='Enter the repository ID',
              help='The ID of the repository to use.')
@click.option('-t', '--rec_type', prompt='Enter the record type',
              help='The record type to use.')
@click.option('-f', '--field', prompt='Enter the field',
              help='The field to extract.')
@click.pass_context
def report(ctx, repo_id, rec_type, field):
    as_ops = ctx.obj['as_ops']
    start_time = ctx.obj['start_time']
    log_suffix = ctx.obj['log_suffix']
    endpoint = as_ops.create_endpoint(rec_type, repo_id)
    ids = as_ops.get_all_records(endpoint)
    for id in ids:
        uri = f'{endpoint}/{id}'
        rec_obj = as_ops.get_record(uri)
        coll_id = models.concat_id(rec_obj)
        report_dict = {'uri': rec_obj['uri'], 'title': rec_obj['title'],
                       'id': coll_id}
        if field in note_type_fields:
            report_dicts = models.extract_note_field(field, rec_obj,
                                                     report_dict)
            for report_dict in report_dicts:
                logger.info(**report_dict)
        elif field in obj_field_dict.keys():
            report_dicts = models.extract_obj_field(field, rec_obj,
                                                    obj_field_dict,
                                                    report_dict)
            for report_dict in report_dicts:
                logger.info(**report_dict)
        else:
            report_dict[field] = rec_obj.get(field, '')
            logger.info(**report_dict)
    models.elapsed_time(start_time, 'Total runtime:')
    models.create_csv_from_log(f'{rec_type}-{field}-values', log_suffix)


@main.command()
@click.pass_context
@click.argument('search')
@click.option('-d', '--dry_run', prompt='Dry run?', default=True,
              help='Perform dry run that does not modify any records.')
@click.option('-i', '--repo_id', prompt='Enter the repository ID',
              help='The ID of the repository to use.')
@click.option('-t', '--rec_type', prompt='Enter the record type',
              help='The record type to use.')
@click.option('-f', '--field', prompt='Enter the field',
              help='The field to edit.')
@click.option('-r', '--rpl_value', prompt='Enter the replacement value',
              help='The replacement value to be inserted.')
def find(ctx, dry_run, repo_id, rec_type, field, search, rpl_value):
    as_ops = ctx.obj['as_ops']
    start_time = ctx.obj['start_time']
    log_suffix = ctx.obj['log_suffix']
    skipped_aos = []
    if rec_type == 'archival_object':
        for uri in skipped_resources:
            aolist = as_ops.get_aos_for_resource(uri)
            skipped_aos.append(aolist)
    skipped_uris = skipped_resources + skipped_aos
    for uri in as_ops.search(search, repo_id, rec_type, field):
        if uri not in skipped_uris:
            rec_obj = as_ops.get_record(uri)
            if field in note_type_fields:
                notes = models.filter_note_type(rec_obj, field)
                for note in notes:
                    for subnote in note.get('subnotes', []):
                        if 'content' in subnote.keys():
                            update = subnote['content'].replace(search,
                                                                rpl_value)
                            subnote['content'] = update
                        elif 'definedlist' in subnote.keys():
                            update = subnote['definedlist'].replace(search,
                                                                    rpl_value)
                            subnote['definedlist'] = update
            else:
                update = rec_obj.get(field, '').replace(search, rpl_value)
                rec_obj[field] = update
            if rec_obj.modified is True:
                as_ops.save_record(rec_obj, dry_run)
        else:
            logger.info(f'{uri} skipped')
    models.elapsed_time(start_time, 'Total runtime:')
    models.create_csv_from_log(f'{rec_type}-{field}-find', log_suffix)


@main.command()
@click.pass_context
@click.option('-d', '--dry_run', prompt='Dry run?', default=True,
              help='Perform dry run that does not modify any records.')
@click.option('-m', '--mapping_csv', prompt='Enter the mapping CSV file',
              help='The mapping CSV file to use.')
def updatedigobj(ctx, dry_run, mapping_csv):
    as_ops = ctx.obj['as_ops']
    start_time = ctx.obj['start_time']
    log_suffix = ctx.obj['log_suffix']
    with open(mapping_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            do_uri = row['do_uri']
            link = row['link']
            dig_obj = as_ops.get_record(do_uri)
            upd_dig_obj = as_ops.update_dig_obj_link(dig_obj, link)
            if upd_dig_obj.modified is True:
                as_ops.save_record(upd_dig_obj, dry_run)
    models.elapsed_time(start_time, 'Total runtime:')
    models.create_csv_from_log('dig_obj', log_suffix)


@main.command()
@click.pass_context
@click.option('-m', '--mapping_csv', prompt='Enter the mapping CSV file',
              help='The mapping CSV file to use.')
@click.option('-i', '--repo_id', prompt='Enter the repository ID',
              help='The ID of the repository to use.')
def newaos(ctx, mapping_csv, repo_id):
    as_ops = ctx.obj['as_ops']
    start_time = ctx.obj['start_time']
    log_suffix = ctx.obj['log_suffix']
    with open(mapping_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            agent_link = as_ops.create_agent_link(row['publisher'], 'creator',
                                                  'pbl')
            new_dig_obj = as_ops.create_dig_obj(row['title'], row['link'])
            note = as_ops.create_note('scopecontent',
                                      'Scope and Contents of the Collection',
                                      row['abstract'])
            arch_obj = as_ops.create_arch_obj(row['title'], 'file',
                                              [agent_link], [note],
                                              row['parent_uri'],
                                              row['resource'])
            do_endpoint = as_ops.create_endpoint('digital_object', repo_id)
            do_resp = as_ops.post_new_record(new_dig_obj, do_endpoint)
            arch_obj = as_ops.link_dig_obj(arch_obj, do_resp['uri'])
            dig_obj = as_ops.get_record(do_resp['uri'])
            upd_dig_obj = as_ops.update_dig_obj_link(dig_obj, row['link'])
            as_ops.save_record(upd_dig_obj, 'False')
            ao_endpoint = as_ops.create_endpoint('archival_object', repo_id)
            ao_resp = as_ops.post_new_record(arch_obj, ao_endpoint)
    models.elapsed_time(start_time, 'Total runtime:')
    models.create_csv_from_log('dig_obj', log_suffix)


if __name__ == '__main__':
    main()
