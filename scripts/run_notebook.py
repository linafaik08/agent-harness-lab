"""Executes the harness ladder notebook and saves it with its outputs.

The notebook reads HARNESS_TASKS from the environment, so the same script
serves the quick demo and the full run. Execution goes through nbclient
directly, which keeps it independent of any local Jupyter config. The OpenAI
key is checked first, after the repository's .env file has been read, so a
missing key fails in a second rather than inside the first trial.

Usage:
    python scripts/run_notebook.py [--output path/to/executed.ipynb]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

import agent_harness_lab.models  # noqa: F401  Importing it loads the .env file.

NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "harness_ladder.ipynb"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=NOTEBOOK, help="Where to save the executed notebook.")
    args = parser.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set. Copy .env.example to .env and add the key there.")

    notebook = nbformat.read(NOTEBOOK, as_version=4)
    NotebookClient(notebook, timeout=None, kernel_name="python3",
                   resources={"metadata": {"path": str(NOTEBOOK.parent)}}).execute()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, args.output)
    print(f"Executed notebook saved to {args.output}")


if __name__ == "__main__":
    main()
