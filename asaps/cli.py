import click
import models
from asnake.client import ASnakeClient


@click.command()
@click.option('--url', envvar='ARCHIVESSPACE_URL')
@click.option('-u', '--username', prompt='Enter username',
              help='The username for authentication.')
@click.option('-p', '--password', prompt='Enter password',
              hide_input=True,
              help='The password for authentication.')
def main(url, username, password):
    client = ASnakeClient(baseurl=url, username=username,
                          password=password)
    as_ops = models.AsOperations(client)
    record = as_ops.get_record('/repositories/2/resources/423')
    print(record)


if __name__ == '__main__':
    main()
