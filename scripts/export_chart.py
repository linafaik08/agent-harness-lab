"""Renders a run's saved ladder chart to a static PNG for the README.

The notebook saves the figure as `ladder.json`. Rendering it here, in a fresh
process, keeps Kaleido and its headless Chrome out of the notebook kernel,
where exports after a long run were observed to take over twenty minutes.

Usage:
    python scripts/export_chart.py results/gpt-6-luna_10tasks
"""

from __future__ import annotations

import argparse
from pathlib import Path

import plotly.io as pio


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path, help="A run folder such as results/gpt-6-luna_10tasks.")
    args = parser.parse_args()

    figure = pio.read_json(args.run_dir / "ladder.json")
    figure.write_image(args.run_dir / "ladder.png", scale=2)
    print(f"Chart saved to {args.run_dir / 'ladder.png'}")


if __name__ == "__main__":
    main()
