from agent_harness_lab.workspace import changed_files, fingerprint, run_command, snapshot


def test_timeout_is_reported(tmp_path):
    result = run_command("sleep 5", tmp_path, timeout_s=0.5)
    assert result.timed_out and result.exit_code == 124


def test_output_combines_stdout_and_stderr(tmp_path):
    result = run_command("echo out; echo err >&2; exit 3", tmp_path)
    assert result.exit_code == 3
    assert "out" in result.output and "err" in result.output


def test_snapshot_diff_lists_created_modified_and_deleted_files(tmp_path):
    (tmp_path / "keep.txt").write_text("a")
    (tmp_path / "edit.txt").write_text("a")
    (tmp_path / "gone.txt").write_text("a")
    before = snapshot(tmp_path)
    (tmp_path / "edit.txt").write_text("b")
    (tmp_path / "gone.txt").unlink()
    (tmp_path / "new.txt").write_text("a")
    after = snapshot(tmp_path)
    assert changed_files(before, after) == ["edit.txt", "gone.txt", "new.txt"]
    assert fingerprint(before) != fingerprint(after)
