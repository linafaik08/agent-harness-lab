from agent_harness_lab.grading import grade
from agent_harness_lab.tasks import task_workspace


def test_editing_the_visible_test_does_not_fool_the_grader(tasks):
    task = tasks[1]
    with task_workspace(task) as workspace:
        test_file = workspace / task.visible_test
        test_file.write_text(test_file.read_text().replace("assert ", "assert True or "))
        assert not grade(task, workspace).passed
