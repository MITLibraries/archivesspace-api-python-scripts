from asnake.client import ASnakeClient
import click
import importlib
import csv
import datetime
import time
import json

# main
@click.group()
@click.option('-s', '--secfile',
              prompt='Enter the name of the secrets file to use, omit ".py"',
              help='The name of the secrets file to use', default='secrets')
@click.pass_context
def asmain(ctx, secfile):
    """Select secrets.py file for the appropriate ArchivesSpace instance."""
    starttime = time.time()
    nologs = ['downloadjson']
    headerdict = {'extractid': ['uri'] + ['id']}
    secfileExists = importlib.util.find_spec(secfile)
    if secfileExists is not None:
        secrets = __import__(secfile)
    else:
        secrets = __import__('secrets')
    print('Editing ' + secfile + ' ' + secrets.baseURL)
    client = ASnakeClient(baseurl=secrets.baseURL,
                          username=secrets.user,
                          password=secrets.password)
    client.authorize()
    ctx.obj = dict()
    ctx.obj['starttime'] = starttime
    ctx.obj['nologs'] = nologs
    ctx.obj['client'] = client
    ctx.obj['headerdict'] = headerdict

# operation commands
@asmain.command()
@click.option('-i', '--repoid',
              prompt='Enter the repository id',
              help='The repository id to use', default=2)
@click.option('-t', '--rectype',
              prompt='Enter the record type',
              help='The record type to retrieve', default='')
@click.option('-o', '--output',
              prompt='Enter the output to run as the records are retrieved',
              help='The output to run once the records are retrieved',
              default='')
@click.pass_context
def getallrecords(ctx, repoid, rectype, output):
    """Retrieve records of a specified type."""
    agents = ['corporate_entities', 'families', 'people', 'software']
    nonrepo = ['locations', 'subjects']
    nologs = ctx.obj['nologs']
    client = ctx.obj['client']
    ctx.obj['repoid'] = repoid
    if rectype in agents:
        endpt = 'agents/' + rectype
    elif rectype in nonrepo:
        endpt = rectype
    else:
        endpt = 'repositories/' + str(repoid) + '/' + rectype
    ctx.obj['endpt'] = endpt
    allendpt = endpt + '?all_ids=true'
    ids = client.get(allendpt).json()
    if output not in nologs:
        filename = rectype + '-' + output
        ctx.invoke(createcsv, filename=filename, output=output)
    ctx.invoke(iterateids, ids=ids, output=output)
    ctx.invoke(elapsedtime)


@asmain.command()
@click.option('-u', '--uri',
              help='The record uri to retrieve', default='')
@click.option('-o', '--output',
              prompt='Enter the output to run once the record is retrieved: ',
              help='The output to run once the record is retrieved',
              default='')
@click.pass_context
def getrecord(ctx, uri, output):
    """Retrieve an individual record."""
    client = ctx.obj['client']
    record = client.get(uri).json()
    ctx.obj['record'] = record
    output = eval(output)
    ctx.invoke(output, uri=uri)


# component commands
@asmain.command()
@click.pass_context
def createcsv(ctx, filename, output):
    """Create CSV file of retrived data."""
    date = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    f = csv.writer(open(filename + date + '.csv', 'w'))
    header = ctx.obj['headerdict'][output]
    f.writerow(header)
    ctx.obj['f'] = f


@click.pass_context
def elapsedtime(ctx):
    """Generate elapsed time."""
    starttime = ctx.obj['starttime']
    label = 'Elapsed time'
    td = datetime.timedelta(seconds=time.time() - starttime)
    print(label + ': {}'.format(td))


@asmain.command()
@click.pass_context
def iterateids(ctx, ids, output):
    """Iterate through a list of AS ids and retrieves each record."""
    endpt = ctx.obj['endpt']
    with click.progressbar(ids) as bar:
        for id in bar:
            uri = endpt + '/' + str(id)
            ctx.obj['uri'] = uri
            ctx.invoke(getrecord, uri=uri, output=output)


# output commands
@asmain.command()
@click.pass_context
def extractid(ctx, uri):
    """Extract concatenated ID from record."""
    record = ctx.obj['record']
    f = ctx.obj['f']
    id_0 = record.get('id_0', '')
    id_1 = record.get('id_1', '')
    if id_1 != '':
        id_1 = '-' + id_1
    id_2 = record.get('id_2', '')
    if id_2 != '':
        id_2 = '-' + id_2
    id_3 = record.get('id_3', '')
    if id_3 != '':
        id_3 = '-' + id_3
    concatid = id_0 + id_1 + id_2 + id_3
    row = ([uri] + [concatid])
    f.writerow(row)


@asmain.command()
@click.pass_context
def downloadjson(ctx, uri):
    """Download a JSON file."""
    record = ctx.obj['record']
    filename = uri[1:len(uri)].replace('/', '-')
    f = open(filename + '.json', 'w')
    json.dump(record, f)
    f.close()


if __name__ == '__main__':
    asmain()
