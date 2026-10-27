"""Hidden-test grading, run once the agent has stopped."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from agent_harness_lab.tasks import Task


@dataclass(frozen=True)
class GradeResult:
    passed: bool
    output: str


def grade(task: Task, workspace: Path, timeout_s: float = 60) -> GradeResult:
    """Runs the task's hidden tests against the code the agent left behind.

    The hidden test file stays in the task directory and pytest starts from an
    empty temporary directory, with the workspace placed on PYTHONPATH. The
    agent's own copy of the tests, edited or not, therefore plays no part in the
    verdict.
    """
    env = {**os.environ, "PYTHONPATH": str(workspace), "PYTHONDONTWRITEBYTECODE": "1"}
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(task.hidden_test)]
    with tempfile.TemporaryDirectory(prefix="harness-grade-") as run_dir:
        try:
            proc = subprocess.run(cmd, cwd=run_dir, env=env, capture_output=True, text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return GradeResult(passed=False, output=f"grader timed out after {timeout_s}s")
    return GradeResult(passed=proc.returncode == 0, output=proc.stdout + proc.stderr)
