"""Every task must be a fair puzzle: broken as shipped, solved by its reference fix."""

import pytest

from agent_harness_lab.grading import grade
from agent_harness_lab.tasks import load_tasks, task_workspace
from agent_harness_lab.workspace import run_command

TASKS = load_tasks()


def apply_reference_fix(task, workspace):
    path = workspace / task.fix["path"]
    path.write_text(path.read_text().replace(task.fix["old"], task.fix["new"], 1))


def test_there_are_ten_tasks():
    assert len(TASKS) == 10


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_visible_and_hidden_tests_fail_before_the_fix(task):
    with task_workspace(task) as workspace:
        assert run_command("python -m pytest -q", workspace).exit_code != 0
        assert not grade(task, workspace).passed


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_reference_fix_passes_visible_and_hidden_tests(task):
    with task_workspace(task) as workspace:
        apply_reference_fix(task, workspace)
        assert run_command("python -m pytest -q", workspace).exit_code == 0
        assert grade(task, workspace).passed


def test_hidden_tests_stay_outside_the_workspace(tasks):
    task = tasks[0]
    with task_workspace(task) as workspace:
        assert not list(workspace.rglob("test_hidden.py"))
        assert workspace not in task.hidden_test.parents


def test_workspace_is_deleted_afterwards(tasks):
    with task_workspace(tasks[0]) as workspace:
        pass
    assert not workspace.exists()
