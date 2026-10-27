"""Saving and loading per-trial transcripts."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path


def save_transcript(run_dir: Path, record: dict) -> Path:
    """Writes one trial record to `<run_dir>/transcripts/<version>/<task>/trial_<n>.json`.

    The record must carry the keys "version", "task" and "trial"; everything
    else is stored as given.
    """
    path = run_dir / "transcripts" / record["version"] / record["task"] / f"trial_{record['trial']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, default=str))
    return path


def load_transcripts(run_dir: Path) -> Iterator[dict]:
    """Yields every saved trial record under `run_dir`, in path order."""
    for path in sorted((run_dir / "transcripts").glob("*/*/trial_*.json")):
        yield json.loads(path.read_text())
