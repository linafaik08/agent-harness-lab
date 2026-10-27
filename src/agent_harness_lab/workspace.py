"""Shell execution inside a workspace, and snapshots that reveal what changed."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# A guard against runaway output, far above anything a harness would show a model.
# Truncation as a deliberate design choice is a harness component, not plumbing.
HARD_OUTPUT_LIMIT = 100_000
IGNORED_PARTS = {"__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class CommandResult:
    """Outcome of one shell command."""

    command: str
    exit_code: int
    output: str
    timed_out: bool
    duration_s: float


def run_command(command: str, cwd: Path, timeout_s: float = 30) -> CommandResult:
    """Runs a shell command in `cwd` and captures stdout and stderr together.

    The project's interpreter is placed first on PATH, so `python` and `pytest`
    inside the command resolve to the same environment as the notebook. A command
    that exceeds `timeout_s` is killed and reported with exit code 124. This is
    not a sandbox: the command runs with the caller's permissions.
    """
    env = {**os.environ, "PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command, shell=True, cwd=cwd, env=env, capture_output=True,
            text=True, timeout=timeout_s, stdin=subprocess.DEVNULL,
        )
        output, exit_code, timed_out = proc.stdout + proc.stderr, proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        partial = (exc.stdout or b"") + (exc.stderr or b"")
        partial = partial.decode(errors="replace") if isinstance(partial, bytes) else partial
        output, exit_code, timed_out = partial + f"\n[command timed out after {timeout_s}s]", 124, True
    return CommandResult(
        command=command,
        exit_code=exit_code,
        output=output[:HARD_OUTPUT_LIMIT],
        timed_out=timed_out,
        duration_s=round(time.monotonic() - start, 3),
    )


def snapshot(root: Path) -> dict[str, str]:
    """Maps every file under `root` to a hash of its content, skipping caches."""
    hashes = {}
    for path in root.rglob("*"):
        if path.is_file() and not IGNORED_PARTS.intersection(path.parts):
            hashes[str(path.relative_to(root))] = hashlib.sha1(path.read_bytes()).hexdigest()
    return hashes


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """Lists files that were created, modified or deleted between two snapshots."""
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def fingerprint(files: dict[str, str]) -> str:
    """Condenses a snapshot into one short, stable digest of the whole workspace."""
    joined = "\n".join(f"{path}:{digest}" for path, digest in sorted(files.items()))
    return hashlib.sha1(joined.encode()).hexdigest()[:12]
