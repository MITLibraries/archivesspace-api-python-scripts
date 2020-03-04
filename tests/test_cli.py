from click.testing import CliRunner
import pytest
import requests_mock

from asaps.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_report(runner):
    """Test report command."""


def test_find(runner):
    """Test find command."""
    with requests_mock.Mocker() as m:
        json_object1 = {'session': 'abcdefg1234567'}
        json_object2 = {'uri': '/repositories/0/resources/1234', 'notes':
                        [{'type': 'acqinfo', 'subnotes': [{'content':
                         'test value'}]}]}
        json_object3 = {'status': 'Updated'}
        base_url = 'mock://mock.mock/users/test/login'
        search_url = f'/repositories/0/search?'
        item_url = f'/repositories/0/resources/1234'
        m.post(base_url, json=json_object1)
        m.get(search_url, json=[json_object2])
        m.get(item_url, json=json_object2)
        m.post(item_url, json=json_object3)
        result = runner.invoke(main,
                               ['--url', 'mock://mock.mock',
                                '--username', 'test',
                                '--password', 'testpass',
                                'find',
                                'test value',
                                '--dry_run', 'False',
                                '--repo_id', '0',
                                '--rec_type', 'resource',
                                '--field', 'acqinfo',
                                '--rpl_value', 'REPLACED',
                                ])
        assert result.exit_code == 0


def test_updatedigobj(runner):
    """Test report command."""
