from asaps.cli import main


def test_deletefield(runner):
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
            "--modify_records",
            "--metadata_csv",
            "tests/fixtures/deletefield.csv",
            "--field",
            "accessrestrict",
        ],
    )
    assert result.exit_code == 0


def test_find(runner):
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
            "--search",
            "test value",
            "--modify_records",
            "--repository_id",
            "0",
            "--record_type",
            "resource",
            "--field",
            "acqinfo",
            "--replacement_value",
            "REPLACED",
        ],
    )
    assert result.exit_code == 0


def test_metadata(runner):
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
            "--repository_id",
            "0",
        ],
    )
    assert result.exit_code == 0


def test_newagents(runner, output_dir):
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
            "--repository_id",
            "0",
            "--metadata_csv",
            "tests/fixtures/newarchobjs.csv",
            "--agent_file",
            "tests/fixtures/newarchobjs-agents.csv",
        ],
    )
    assert result.exit_code == 0


def test_newdigobjs(runner):
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
            "--repository_id",
            "0",
        ],
    )
    assert result.exit_code == 0


def test_report(runner):
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
            "--repository_id",
            "0",
            "--record_type",
            "resource",
            "--field",
            "acqinfo",
        ],
    )
    assert result.exit_code == 0


def test_updatedigobj(runner):
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
            "--modify_records",
            "--metadata_csv",
            "tests/fixtures/updatedigobj.csv",
        ],
    )
    assert result.exit_code == 0


def test_updaterecords(runner):
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
            "--modify_records",
            "--metadata_csv",
            "tests/fixtures/updaterecords.csv",
            "--field",
            "accessrestrict",
            "--replacement_value_column",
            "accessrestrict",
        ],
    )
    assert result.exit_code == 0
