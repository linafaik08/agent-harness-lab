"""Bug-fix tasks and the throwaway workspaces the agent works in."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

TASKS_DIR = Path(__file__).resolve().parents[2] / "tasks"


@dataclass(frozen=True)
class Task:
    """One bug-fix task.

    Attributes:
        id: Directory name of the task, such as "02_median".
        issue: The bug report handed to the agent.
        module: Source file that contains the bug, relative to the repository.
        visible_test: Test file the agent can see and run.
        fix: Reference fix as {"path", "old", "new"}. Only the integrity tests
            read it; it never reaches the workspace.
        root: Task directory holding `repo/`, `hidden/` and `task.json`.
    """

    id: str
    issue: str
    module: str
    visible_test: str
    fix: dict
    root: Path

    @property
    def repo_dir(self) -> Path:
        return self.root / "repo"

    @property
    def hidden_test(self) -> Path:
        return self.root / "hidden" / "test_hidden.py"


def load_tasks(limit: int | None = None, tasks_dir: Path = TASKS_DIR) -> list[Task]:
    """Loads tasks in directory order.

    Args:
        limit: Number of tasks to keep from the start of the list; None keeps all.
        tasks_dir: Directory containing one sub-directory per task.

    Returns:
        The tasks, sorted by id.
    """
    tasks = []
    for meta_path in sorted(tasks_dir.glob("*/task.json")):
        meta = json.loads(meta_path.read_text())
        tasks.append(Task(root=meta_path.parent, **meta))
    return tasks[:limit] if limit else tasks


@contextmanager
def task_workspace(task: Task) -> Iterator[Path]:
    """Yields a fresh temporary copy of the task repository.

    The copy lives under the system temp directory, so the hidden grader tests,
    which stay in the task directory, are never inside it. The copy is deleted
    when the context exits.
    """
    parent = Path(tempfile.mkdtemp(prefix=f"harness-{task.id}-"))
    workspace = parent / "repo"
    shutil.copytree(task.repo_dir, workspace)
    try:
        yield workspace
    finally:
        shutil.rmtree(parent, ignore_errors=True)
