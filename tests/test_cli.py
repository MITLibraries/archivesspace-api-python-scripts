from click.testing import CliRunner
import csv
import pytest
import requests_mock

from asaps.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_deletefield(runner):
    """Test updaterecords command."""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('metadata.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['uri'])
                writer.writerow(['/repositories/0/archival_objects/1234'])
                session_json = {'session': 'abcdefg1234567'}
                ao_json = {'uri': '/repositories/0/archival_objects/1234',
                           'notes': [{'subnotes': [{'content':
                                                   'Old note content'}]}]}
                ao_upd_json = {'status': 'Updated'}
                base_url = 'mock://mock.mock/users/test/login'
                item_url = '/repositories/0/archival_objects/1234'
                m.post(base_url, json=session_json)
                m.get(item_url, json=ao_json)
                m.post(item_url, json=ao_upd_json)
                result = runner.invoke(main,
                                       ['--url', 'mock://mock.mock',
                                        '--username', 'test',
                                        '--password', 'testpass',
                                        'deletefield',
                                        '--dry_run', 'False',
                                        '--metadata_csv', 'metadata.csv',
                                        '--field', 'accessrestrict'
                                        ])
        assert result.exit_code == 0


def test_find(runner):
    """Test find command."""
    with requests_mock.Mocker() as m:
        session_json = {'session': 'abcdefg1234567'}
        ao_json = {'uri': '/repositories/0/resources/1234', 'notes':
                   [{'type': 'acqinfo', 'subnotes': [{'content':
                    'test value'}]}]}
        ao_upd_json = {'status': 'Updated'}
        base_url = 'mock://mock.mock/users/test/login'
        search_url = '/repositories/0/search?'
        item_url = '/repositories/0/resources/1234'
        m.post(base_url, json=session_json)
        m.get(search_url, json=[ao_json])
        m.get(item_url, json=ao_json)
        m.post(item_url, json=ao_upd_json)
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


def test_metadata(runner):
    """Test metadata command"""
    with requests_mock.Mocker() as m:
        session_json = {'session': 'abcdefg1234567'}
        res_json = {'uri': '/repositories/0/resources/1234', 'ref_id':
                    'a1b_2c3'}
        base_url = 'mock://mock.mock/users/test/login'
        item_url = '/repositories/0/resources/1234/tree'
        m.post(base_url, json=session_json)
        m.get(item_url, json=res_json)
        result = runner.invoke(main,
                               ['--url', 'mock://mock.mock',
                                '--username', 'test',
                                '--password', 'testpass',
                                'metadata',
                                '--resource', '1234',
                                '--file_identifier', 'ref_id', '--repo_id', '0'
                                ])
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
                writer.writerow(['Smith, J.'] + ['people'] + ['Smith']
                                + ['Smith, John, 1902-2049']
                                + ['mock://mock.mock/123'] + ['John']
                                + [''] + [''] + [''] + [''] + ['1902-2049']
                                + ['1902'] + ['2049'] + [''] + ['existence'])
            session_json = {'session': 'abcdefg1234567'}
            ag_crtd_json = {'status': 'Created', 'uri':
                            '/agents/people/789'}
            base_url = 'mock://mock.mock/users/test/login'
            agent_url = '/agents/people'
            m.post(base_url, json=session_json)
            m.post(agent_url, json=ag_crtd_json)
            result = runner.invoke(main,
                                   ['--url', 'mock://mock.mock',
                                    '--username', 'test',
                                    '--password', 'testpass',
                                    'newagents', '--metadata_csv',
                                    'metadata.csv', '--match_point', 'search'])
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
                session_json = {'session': 'abcdefg1234567'}
                do_crtd_json = {'status': 'Created', 'uri':
                                '/repositories/0/digital_objects/789'}
                do_json = {'uri': '/repositories/0/digital_objects/789',
                           'file_versions': [{'file_uri':
                                             'old_content_link'}]}
                ao_upd_json = {'status': 'Updated'}
                ao_crtd_json = {'status': 'Created', 'uri':
                                '/repositories/0/archival_objects/123'}
                base_url = 'mock://mock.mock/users/test/login'
                do_url = '/repositories/0/digital_objects'
                item_url = '/repositories/0/digital_objects/789'
                arch_obj_url = '/repositories/0/archival_objects'
                m.post(base_url, json=session_json)
                m.post(do_url, json=do_crtd_json)
                m.get(item_url, json=do_json)
                m.post(item_url, json=ao_upd_json)
                m.post(arch_obj_url, json=ao_crtd_json)
                result = runner.invoke(main,
                                       ['--url', 'mock://mock.mock',
                                        '--username', 'test',
                                        '--password', 'testpass',
                                        'newarchobjs',
                                        '--repo_id', '0',
                                        '--metadata_csv', 'metadata.csv',
                                        '--agent_file', 'agents.csv'])
    assert result.exit_code == 0


def test_newdigobjs(runner):
    """Test newdigobjs command"""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('ingest.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['uri'] + ['display_string'] + ['link'])
                writer.writerow(['/repositories/0/archival_objects/123']
                                + ['AO Title']
                                + ['mock://example.com/handle/111.1111'])

                session_json = {'session': 'abcdefg1234567'}
                do_crtd_json = {'status': 'Created', 'uri':
                                '/repositories/0/digital_objects/789'}
                do_json = {'uri': '/repositories/0/digital_objects/789',
                           'file_versions': [
                                        {'file_uri':
                                         'mock://example.com/handle/111.1111'}]
                           }
                do_upd_json = {'status': 'Updated'}
                ao_upd_json = {'status': 'Updated', 'uri':
                               '/repositories/0/archival_objects/123'}
                base_url = 'mock://mock.mock/users/test/login'
                do_url = '/repositories/0/digital_objects'
                item_url = '/repositories/0/digital_objects/789'
                arch_obj_url = '/repositories/0/digital_objects'
                m.post(base_url, json=session_json)
                m.post(do_url, json=do_crtd_json)
                m.get(item_url, json=do_json)
                m.post(item_url, json=do_upd_json)
                m.post(arch_obj_url, json=ao_upd_json)
                result = runner.invoke(main,
                                       ['--url', 'mock://mock.mock',
                                        '--username', 'test',
                                        '--password', 'testpass',
                                        'newdigobjs',
                                        '--metadata_csv', 'ingest.csv',
                                        '--repo_id', '0',
                                        ])
    assert result.exit_code == 0


def test_report(runner):
    """Test report command."""
    with requests_mock.Mocker() as m:
        session_json = {'session': 'abcdefg1234567'}
        res_json = {'id_0': 'AB', 'id_1': '123', 'title': 'Test title',
                    'uri': '/repositories/0/resources/1234', 'notes':
                        [{'type': 'acqinfo', 'subnotes': [{'content':
                         'test value'}]}]}
        base_url = 'mock://mock.mock/users/test/login'
        ids_url = '/repositories/0/resources?all_ids=true'
        item_url = '/repositories/0/resources/1234'
        m.post(base_url, json=session_json)
        m.get(ids_url, json=['1234'])
        m.get(item_url, json=res_json)
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


def test_updatedigobj(runner):
    """Test updatedigobj command."""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('metadata.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['do_uri'] + ['link'])
                writer.writerow(['/repositories/0/digital_objects/1234'] +
                                ['new_content_link'])
            session_json = {'session': 'abcdefg1234567'}
            do_json = {'uri': '/repositories/0/digital_objects/1234',
                       'file_versions': [{'file_uri':
                                         'old_content_link'}]}
            do_upd_json = {'status': 'Updated'}
            base_url = 'mock://mock.mock/users/test/login'
            item_url = '/repositories/0/digital_objects/1234'
            m.post(base_url, json=session_json)
            m.get(item_url, json=do_json)
            m.post(item_url, json=do_upd_json)
            result = runner.invoke(main,
                                   ['--url', 'mock://mock.mock',
                                    '--username', 'test',
                                    '--password', 'testpass',
                                    'updatedigobj',
                                    '--dry_run', 'False',
                                    '--metadata_csv', 'metadata.csv'
                                    ])
    assert result.exit_code == 0


def test_updaterecords(runner):
    """Test updaterecords command."""
    with requests_mock.Mocker() as m:
        with runner.isolated_filesystem():
            with open('metadata.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['uri'] + ['accessrestrict'])
                writer.writerow(['/repositories/0/archival_objects/1234'] +
                                ['New note content'])
                session_json = {'session': 'abcdefg1234567'}
                ao_json = {'uri': '/repositories/0/archival_objects/1234',
                           'notes': [{'subnotes': [{'content':
                                                   'Old note content'}]}]}
                ao_upd_json = {'status': 'Updated'}
                base_url = 'mock://mock.mock/users/test/login'
                item_url = '/repositories/0/archival_objects/1234'
                m.post(base_url, json=session_json)
                m.get(item_url, json=ao_json)
                m.post(item_url, json=ao_upd_json)
                result = runner.invoke(main,
                                       ['--url', 'mock://mock.mock',
                                        '--username', 'test',
                                        '--password', 'testpass',
                                        'updaterecords',
                                        '--dry_run', 'False',
                                        '--metadata_csv', 'metadata.csv',
                                        '--field', 'accessrestrict',
                                        '--rpl_value_col', 'accessrestrict'
                                        ])
        assert result.exit_code == 0
