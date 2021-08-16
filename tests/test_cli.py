from asaps.cli import main


def test_deletefield(runner):
    """Test updaterecords command."""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "deletefield",
            "--dry_run",
            "False",
            "--metadata_csv",
            "tests/fixtures/deletefield.csv",
            "--field",
            "accessrestrict",
        ],
    )
    assert result.exit_code == 0


def test_find(runner):
    """Test find command."""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "find",
            "test value",
            "--dry_run",
            "False",
            "--repo_id",
            "0",
            "--rec_type",
            "resource",
            "--field",
            "acqinfo",
            "--rpl_value",
            "REPLACED",
        ],
    )
    assert result.exit_code == 0


def test_metadata(runner):
    """Test metadata command"""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "metadata",
            "--resource",
            "423",
            "--file_identifier",
            "ref_id",
            "--repo_id",
            "0",
        ],
    )
    assert result.exit_code == 0


def test_newagents(runner, output_dir):
    """Test newagents command."""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "newagents",
            "--metadata_csv",
            "tests/fixtures/newagents.csv",
            "--output_path",
            output_dir,
            "--match_point",
            "search",
        ],
    )
    assert result.exit_code == 0


def test_newarchobjs(runner):
    """Test newarchobjs command."""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "newarchobjs",
            "--repo_id",
            "0",
            "--metadata_csv",
            "tests/fixtures/newarchobjs.csv",
            "--agent_file",
            "tests/fixtures/newarchobjs-agents.csv",
        ],
    )
    assert result.exit_code == 0


def test_newdigobjs(runner):
    """Test newdigobjs command"""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://mock.mock",
            "--username",
            "test",
            "--password",
            "testpass",
            "newdigobjs",
            "--metadata_csv",
            "tests/fixtures/newdigobjs.csv",
            "--repo_id",
            "0",
        ],
    )
    assert result.exit_code == 0


def test_report(runner):
    """Test report command."""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "report",
            "--repo_id",
            "0",
            "--rec_type",
            "resource",
            "--field",
            "acqinfo",
        ],
    )
    assert result.exit_code == 0


def test_updatedigobj(runner):
    """Test updatedigobj command."""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "updatedigobj",
            "--dry_run",
            "False",
            "--metadata_csv",
            "tests/fixtures/updatedigobj.csv",
        ],
    )
    assert result.exit_code == 0


def test_updaterecords(runner):
    """Test updaterecords command."""
    result = runner.invoke(
        main,
        [
            "--url",
            "mock://example.com",
            "--username",
            "test",
            "--password",
            "testpass",
            "updaterecords",
            "--dry_run",
            "False",
            "--metadata_csv",
            "tests/fixtures/updaterecords.csv",
            "--field",
            "accessrestrict",
            "--rpl_value_col",
            "accessrestrict",
        ],
    )
    assert result.exit_code == 0
