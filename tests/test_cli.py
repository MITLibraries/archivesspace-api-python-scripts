import csv

from asaps.cli import main


def test_deletefield(runner):
    """Test updaterecords command."""
    with runner.isolated_filesystem():
        with open('metadata.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['uri'])
            writer.writerow(['/repositories/0/archival_objects/1234'])
            result = runner.invoke(main,
                                   ['--url', 'mock://example.com',
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
    result = runner.invoke(main,
                           ['--url', 'mock://example.com',
                            '--username', 'test',
                            '--password', 'testpass',
                            'find',
                            'test value',
                            '--dry_run', 'False',
                            '--repo_id', '0',
                            '--rec_type', 'resource',
                            '--field', 'acqinfo',
                            '--rpl_value', 'REPLACED'])
    assert result.exit_code == 0


def test_metadata(runner):
    """Test metadata command"""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com',
                            '--username', 'test',
                            '--password', 'testpass',
                            'metadata',
                            '--resource', '423',
                            '--file_identifier', 'ref_id', '--repo_id', '0'])
    assert result.exit_code == 0


def test_newagents(runner):
    """Test newagents command."""
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
        result = runner.invoke(main,
                               ['--url', 'mock://example.com',
                                '--username', 'test',
                                '--password', 'testpass',
                                'newagents', '--metadata_csv',
                                'metadata.csv', '--match_point', 'search'])
        assert result.exit_code == 0


def test_newarchobjs(runner):
    """Test newarchobjs command."""
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
            result = runner.invoke(main,
                                   ['--url', 'mock://example.com',
                                    '--username', 'test',
                                    '--password', 'testpass',
                                    'newarchobjs',
                                    '--repo_id', '0',
                                    '--metadata_csv', 'metadata.csv',
                                    '--agent_file', 'agents.csv'])
        assert result.exit_code == 0


def test_newdigobjs(runner):
    """Test newdigobjs command"""
    with runner.isolated_filesystem():
        with open('ingest.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['uri'] + ['display_string'] + ['link'])
            writer.writerow(['/repositories/0/archival_objects/123']
                            + ['AO Title']
                            + ['mock://example.com/handle/111.1111'])
            result = runner.invoke(main,
                                   ['--url', 'mock://mock.mock',
                                    '--username', 'test',
                                    '--password', 'testpass',
                                    'newdigobjs',
                                    '--metadata_csv', 'ingest.csv',
                                    '--repo_id', '0'])
        assert result.exit_code == 0


def test_report(runner):
    """Test report command."""
    result = runner.invoke(main,
                           ['--url', 'mock://example.com',
                            '--username', 'test',
                            '--password', 'testpass',
                            'report',
                            '--repo_id', '0',
                            '--rec_type', 'resource',
                            '--field', 'acqinfo'])
    assert result.exit_code == 0


def test_updatedigobj(runner):
    """Test updatedigobj command."""
    with runner.isolated_filesystem():
        with open('metadata.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['do_uri'] + ['link'])
            writer.writerow(['/repositories/0/digital_objects/5678'] +
                            ['new_content_link'])
        result = runner.invoke(main,
                               ['--url', 'mock://example.com',
                                '--username', 'test',
                                '--password', 'testpass',
                                'updatedigobj',
                                '--dry_run', 'False',
                                '--metadata_csv', 'metadata.csv'])
        assert result.exit_code == 0


def test_updaterecords(runner):
    """Test updaterecords command."""
    with runner.isolated_filesystem():
        with open('metadata.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['uri'] + ['accessrestrict'])
            writer.writerow(['/repositories/0/archival_objects/1234'] +
                            ['New note content'])
            result = runner.invoke(main,
                                   ['--url', 'mock://example.com',
                                    '--username', 'test',
                                    '--password', 'testpass',
                                    'updaterecords',
                                    '--dry_run', 'False',
                                    '--metadata_csv', 'metadata.csv',
                                    '--field', 'accessrestrict',
                                    '--rpl_value_col', 'accessrestrict'])
        assert result.exit_code == 0
