from click.testing import CliRunner
import csv
import pytest
import requests_mock

from asaps.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_report(runner):
    """Test report command."""
    with requests_mock.Mocker() as m:
        json_object1 = {'session': 'abcdefg1234567'}
        json_object2 = {'id_0': 'AB', 'id_1': '123', 'title': 'Test title',
                        'uri': '/repositories/0/resources/1234', 'notes':
                        [{'type': 'acqinfo', 'subnotes': [{'content':
                         'test value'}]}]}
        base_url = 'mock://mock.mock/users/test/login'
        ids_url = '/repositories/0/resources?all_ids=true'
        item_url = '/repositories/0/resources/1234'
        m.post(base_url, json=json_object1)
        m.get(ids_url, json=['1234'])
        m.get(item_url, json=json_object2)
        result = runner.invoke(main,
                               ['--url', 'mock://mock.mock',
                                '--username', 'test',
                                '--password', 'testpass',
                                'report',
                                '--repo_id', '0',
                                '--rec_type', 'resource',
                                '--field', 'acqinfo',
                                ])
        assert result.exit_code == 0


def test_find(runner):
    """Test find command."""
    with requests_mock.Mocker() as m:
        json_object1 = {'session': 'abcdefg1234567'}
        json_object2 = {'uri': '/repositories/0/resources/1234', 'notes':
                        [{'type': 'acqinfo', 'subnotes': [{'content':
                         'test value'}]}]}
        json_object3 = {'status': 'Updated'}
        base_url = 'mock://mock.mock/users/test/login'
        search_url = '/repositories/0/search?'
        item_url = '/repositories/0/resources/1234'
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
    """Test updatedigobj command."""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('mapping.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['do_uri'] + ['link'])
                writer.writerow(['/repositories/0/digital_objects/1234'] +
                                ['new_content_link'])
            json_object1 = {'session': 'abcdefg1234567'}
            json_object2 = {'uri': '/repositories/0/digital_objects/1234',
                            'file_versions': [{'file_uri':
                                              'old_content_link'}]}
            json_object3 = {'status': 'Updated'}
            base_url = 'mock://mock.mock/users/test/login'
            item_url = '/repositories/0/digital_objects/1234'
            m.post(base_url, json=json_object1)
            m.get(item_url, json=json_object2)
            m.post(item_url, json=json_object3)
            result = runner.invoke(main,
                                   ['--url', 'mock://mock.mock',
                                    '--username', 'test',
                                    '--password', 'testpass',
                                    'updatedigobj',
                                    '--dry_run', 'False',
                                    '--mapping_csv', 'mapping.csv'
                                    ])
    assert result.exit_code == 0


def test_newarchobjs(runner):
    """Test newarchobjs command."""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('agents.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['match_point'] + ['uri'])
                writer.writerow(['Smith, J.'] + ['agents/people/123'])
                with open('metadata.csv', 'w') as f2:
                    writer2 = csv.writer(f2)
                    writer2.writerow(['resource'] + ['parent_uri'] + ['title']
                                     + ['publisher'] + ['link'] + ['abstract']
                                     + ['top_container_1']
                                     + ['top_container_2'] + ['child_type']
                                     + ['child_indicator'] + ['authors']
                                     + ['begin'] + ['end'] + ['expression']
                                     + ['certainty'] + ['label'])
                    writer2.writerow(['/repositories/0/resources/123']
                                     + ['/repositories/0/archival_objects/456']
                                     + ['Test title']
                                     + ['/agents/corporate_entities/12']
                                     + ['http://dos.com/123']
                                     + ['This is an abstract']
                                     + ['/repositories/0/top_containers/123']
                                     + ['/repositories/0/top_containers/456']
                                     + ['reel'] + ['2'] + ['["Smith, J."]']
                                     + [''] + [''] + [''] + [''] + [''])
                json_object1 = {'session': 'abcdefg1234567'}
                json_object2 = {'status': 'Created', 'uri':
                                '/repositories/0/digital_objects/789'}
                json_object3 = {'uri': '/repositories/0/digital_objects/789',
                                'file_versions': [{'file_uri':
                                                  'old_content_link'}]}
                json_object4 = {'status': 'Updated'}
                json_object5 = {'status': 'Created', 'uri':
                                '/repositories/0/archival_objects/123'}
                base_url = 'mock://mock.mock/users/test/login'
                do_url = '/repositories/0/digital_objects'
                item_url = '/repositories/0/digital_objects/789'
                arch_obj_url = '/repositories/0/archival_objects'
                m.post(base_url, json=json_object1)
                m.post(do_url, json=json_object2)
                m.get(item_url, json=json_object3)
                m.post(item_url, json=json_object4)
                m.post(arch_obj_url, json=json_object5)
                result = runner.invoke(main,
                                       ['--url', 'mock://mock.mock',
                                        '--username', 'test',
                                        '--password', 'testpass',
                                        'newarchobjs',
                                        '--repo_id', '0',
                                        '--metadata_csv', 'metadata.csv',
                                        '--agent_file', 'agents.csv'])
    assert result.exit_code == 0


def test_newagents(runner):
    """Test newagents command."""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('metadata.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['search'] + ['agent_type'] + ['primary_name']
                                + ['sort_name'] + ['authority_id']
                                + ['rest_of_name'] + ['fuller_form']
                                + ['title'] + ['prefix'] + ['suffix']
                                + ['dates'] + ['expression'] + ['begin']
                                + ['end'] + ['certainty'] + ['label'])
                writer.writerow(['Smith, J.'] + ['agent_person'] + ['Smith']
                                + ['Smith, John, 1902-2049']
                                + ['mock://mock.mock/123'] + ['John']
                                + [''] + [''] + [''] + [''] + ['1902-2049']
                                + ['1902'] + ['2049'] + [''] + ['existence'])
            json_object1 = {'session': 'abcdefg1234567'}
            json_object2 = {'status': 'Created', 'uri':
                            '/agents/people/789'}
            base_url = 'mock://mock.mock/users/test/login'
            agent_url = '/agents/people'
            m.post(base_url, json=json_object1)
            m.post(agent_url, json=json_object2)
            result = runner.invoke(main,
                                   ['--url', 'mock://mock.mock',
                                    '--username', 'test',
                                    '--password', 'testpass',
                                    'newagents', '--metadata_csv',
                                    'metadata.csv', '--match_point', 'search'])
    assert result.exit_code == 0
